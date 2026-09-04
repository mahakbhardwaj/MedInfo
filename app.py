import os
import re
from functools import wraps

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
import pytesseract
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.security import check_password_hash, generate_password_hash

from chatbot.chatbot import answer_question
from database.db import init_database
from database.db import get_connection
from ocr.ocr import extract_text, identify_medicine, allowed_image


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "development-only-change-this-secret")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
init_database()


@app.errorhandler(RequestEntityTooLarge)
def file_too_large(error):
    """Show a friendly message when an upload exceeds 5 MB."""
    return render_template("scan.html", error_message="The image is too large. Please choose an image smaller than 5 MB."), 413


def login_required(view):
    """Allow a page only when a user is logged in."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    """Allow a page only when the logged-in user has the ADMIN role."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        if session.get("user_role") != "ADMIN":
            return "Access denied.", 403
        return view(*args, **kwargs)

    return wrapped_view


def medicine_form_data():
    """Read all medicine fields from an admin form."""
    return {
        "name": request.form.get("name", "").strip(),
        "generic_name": request.form.get("generic_name", "").strip(),
        "category": request.form.get("category", "").strip(),
        "general_uses": request.form.get("general_uses", "").strip(),
        "warnings": request.form.get("warnings", "").strip(),
        "side_effects": request.form.get("side_effects", "").strip(),
        "ingredients": request.form.get("ingredients", "").strip(),
        "storage_information": request.form.get("storage_information", "").strip(),
        "interaction_information": request.form.get("interaction_information", "").strip(),
        "source": request.form.get("source", "").strip(),
    }


def medicine_form_is_valid(medicine):
    """Require every medicine field so records stay useful."""
    return all(medicine.values())


@app.route("/")
def home():
    """Display the application's public home page."""
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Create a normal USER account."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm_password:
            flash("Please fill in every field.", "error")
        elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Please enter a valid email address.", "error")
        elif password != confirm_password:
            flash("Passwords do not match.", "error")
        elif len(password) < 6:
            flash("Password must contain at least 6 characters.", "error")
        else:
            connection = get_connection()
            existing_user = connection.execute(
                "SELECT id FROM users WHERE email = ?", (email,)
            ).fetchone()
            if existing_user:
                connection.close()
                flash("An account with that email already exists.", "error")
            else:
                connection.execute(
                    "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, 'USER')",
                    (name, email, generate_password_hash(password)),
                )
                connection.commit()
                connection.close()
                flash("Registration successful. Please log in.", "success")
                return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log in a user and store their ID and role in the session."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        connection = get_connection()
        user = connection.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        connection.close()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            session["user_role"] = user["role"]
            session["user_name"] = user["name"]
            if user["role"] == "ADMIN":
                return redirect("/admin")
            return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.get("/logout")
def logout():
    """Log out the current user."""
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@app.get("/dashboard")
@login_required
def dashboard():
    """Display the logged-in user's dashboard."""
    return render_template("dashboard.html")


@app.route("/scan", methods=["GET", "POST"])
@login_required
def scan_medicine():
    """Read a medicine image in memory and find a database match."""
    detected_text = None
    medicine = None
    error_message = None

    if request.method == "POST":
        uploaded_file = request.files.get("medicine_image")
        if uploaded_file is None or not uploaded_file.filename:
            error_message = "Please choose an image before scanning."
        elif not allowed_image(uploaded_file.filename, uploaded_file.mimetype):
            error_message = "Unsupported file type. Please upload a PNG, JPG, JPEG, or WEBP image."
        else:
            try:
                image_bytes = uploaded_file.read()
                detected_text = extract_text(image_bytes)
                if detected_text:
                    connection = get_connection()
                    medicines = connection.execute("SELECT * FROM medicines ORDER BY length(name) DESC").fetchall()
                    connection.close()
                    medicine = identify_medicine(detected_text, medicines)
            except Exception as error:
                if isinstance(error, pytesseract.TesseractNotFoundError):
                    error_message = "The OCR engine is not installed or configured. Please install Tesseract OCR and try again."
                elif isinstance(error, ValueError):
                    error_message = str(error)
                else:
                    error_message = "The image could not be scanned. Please try a clear, valid image."

    return render_template(
        "scan.html",
        detected_text=detected_text,
        medicine=medicine,
        error_message=error_message,
    )


@app.get("/admin")
@admin_required
def admin():
    """Display basic admin statistics."""
    connection = get_connection()
    statistics = {
        "medicines": connection.execute("SELECT COUNT(*) AS count FROM medicines").fetchone()["count"],
        "users": connection.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"],
        "conversations": connection.execute("SELECT COUNT(*) AS count FROM chat_history").fetchone()["count"],
    }
    connection.close()
    return render_template("admin/dashboard.html", statistics=statistics)


@app.get("/admin/medicines")
@admin_required
def admin_medicines():
    """List all medicines for administrators."""
    connection = get_connection()
    medicines = connection.execute("SELECT * FROM medicines ORDER BY name").fetchall()
    connection.close()
    return render_template("admin/medicines.html", medicines=medicines)


@app.route("/admin/medicines/add", methods=["GET", "POST"])
@admin_required
def admin_add_medicine():
    """Add a medicine to the existing database."""
    medicine = medicine_form_data() if request.method == "POST" else {}
    if request.method == "POST":
        if not medicine_form_is_valid(medicine):
            flash("Please complete every medicine field.", "error")
        else:
            connection = get_connection()
            try:
                connection.execute(
                    """
                    INSERT INTO medicines
                    (name, generic_name, category, general_uses, warnings,
                     side_effects, ingredients, storage_information,
                     interaction_information, source)
                    VALUES (:name, :generic_name, :category, :general_uses, :warnings,
                            :side_effects, :ingredients, :storage_information,
                            :interaction_information, :source)
                    """,
                    medicine,
                )
                connection.commit()
            except Exception:
                connection.close()
                flash("Medicine name already exists or could not be saved.", "error")
            else:
                connection.close()
                flash("Medicine added successfully.", "success")
                return redirect(url_for("admin_medicines"))
    return render_template("admin/medicine_form.html", medicine=medicine, page_title="Add Medicine")


@app.route("/admin/medicines/<int:medicine_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_medicine(medicine_id):
    """Edit all fields for an existing medicine."""
    connection = get_connection()
    existing_medicine = connection.execute(
        "SELECT * FROM medicines WHERE id = ?", (medicine_id,)
    ).fetchone()
    connection.close()
    if existing_medicine is None:
        return "Medicine not found.", 404

    medicine = medicine_form_data() if request.method == "POST" else dict(existing_medicine)
    if request.method == "POST":
        if not medicine_form_is_valid(medicine):
            flash("Please complete every medicine field.", "error")
        else:
            connection = get_connection()
            try:
                connection.execute(
                    """
                    UPDATE medicines SET name=:name, generic_name=:generic_name,
                    category=:category, general_uses=:general_uses, warnings=:warnings,
                    side_effects=:side_effects, ingredients=:ingredients,
                    storage_information=:storage_information,
                    interaction_information=:interaction_information, source=:source,
                    updated_at=CURRENT_TIMESTAMP WHERE id=:id
                    """,
                    {**medicine, "id": medicine_id},
                )
                connection.commit()
            except Exception:
                connection.close()
                flash("Medicine name already exists or could not be updated.", "error")
            else:
                connection.close()
                flash("Medicine updated successfully.", "success")
                return redirect(url_for("admin_medicines"))
    return render_template("admin/medicine_form.html", medicine=medicine, page_title="Edit Medicine")


@app.post("/admin/medicines/<int:medicine_id>/delete")
@admin_required
def admin_delete_medicine(medicine_id):
    """Delete one medicine and leave its history record intact."""
    connection = get_connection()
    deleted = connection.execute(
        "DELETE FROM medicines WHERE id = ?", (medicine_id,)
    ).rowcount
    connection.commit()
    connection.close()
    flash("Medicine deleted." if deleted else "Medicine not found.", "success" if deleted else "error")
    return redirect(url_for("admin_medicines"))


@app.get("/admin/users")
@admin_required
def admin_users():
    """List users without exposing password hashes."""
    connection = get_connection()
    users = connection.execute(
        "SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC"
    ).fetchall()
    connection.close()
    return render_template("admin/users.html", users=users)


@app.get("/admin/chat-statistics")
@admin_required
def admin_chat_statistics():
    """Display simple conversation counts by intent."""
    connection = get_connection()
    intents = connection.execute(
        "SELECT intent, COUNT(*) AS count FROM chat_history GROUP BY intent ORDER BY count DESC"
    ).fetchall()
    connection.close()
    return render_template("admin/chat_statistics.html", intents=intents)


@app.route("/chatbot")
@login_required
def chatbot():
    """Display the chatbot interface."""
    context_medicine = None
    medicine_id = request.args.get("medicine_id", type=int)
    medicine_name = request.args.get("medicine", "").strip()

    if medicine_id is not None:
        connection = get_connection()
        context_medicine = connection.execute(
            "SELECT id, name FROM medicines WHERE id = ?",
            (medicine_id,),
        ).fetchone()
        connection.close()
    elif medicine_name:
        connection = get_connection()
        context_medicine = connection.execute(
            "SELECT id, name FROM medicines WHERE name LIKE ? ORDER BY name LIMIT 1",
            (medicine_name,),
        ).fetchone()
        connection.close()

    return render_template(
        "chatbot.html",
        context_medicine=context_medicine,
    )


@app.post("/api/chat")
def api_chat():
    """Receive a question and return a safe database-backed chatbot answer."""
    if "user_id" not in session:
        return jsonify({"error": "Please log in to use the chatbot."}), 401

    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    medicine_id = data.get("medicine_id")

    if not message:
        return jsonify({
            "answer": "Please enter a question.",
            "medicine": None,
            "intent": "UNKNOWN",
        }), 400

    if not isinstance(medicine_id, int):
        medicine_id = None

    result = answer_question(message, medicine_id)
    history_medicine_id = medicine_id

    if result["medicine"] is not None:
        connection = get_connection()
        medicine = connection.execute(
            "SELECT id FROM medicines WHERE name = ?",
            (result["medicine"],),
        ).fetchone()
        if medicine is not None:
            history_medicine_id = medicine["id"]
        connection.close()

    connection = get_connection()
    connection.execute(
        """
        INSERT INTO chat_history (user_id, medicine_id, question, answer, intent)
        VALUES (?, ?, ?, ?, ?)
        """,
        (session["user_id"], history_medicine_id, message, result["answer"], result["intent"]),
    )
    connection.commit()
    connection.close()

    return jsonify(result)


@app.route("/history")
@login_required
def history():
    """Display saved conversations, newest first."""
    connection = get_connection()
    conversations = connection.execute(
        """
        SELECT chat_history.*, medicines.name AS medicine_name
        FROM chat_history
        LEFT JOIN medicines ON medicines.id = chat_history.medicine_id
        WHERE chat_history.user_id = ?
        ORDER BY chat_history.created_at DESC, chat_history.id DESC
        """,
        (session["user_id"],),
    ).fetchall()
    connection.close()
    return render_template("history.html", history=conversations)


@app.post("/history/clear")
@login_required
def clear_history():
    """Delete only saved chatbot conversations."""
    connection = get_connection()
    connection.execute(
        "DELETE FROM chat_history WHERE user_id = ?",
        (session["user_id"],),
    )
    connection.commit()
    connection.close()
    return render_template("history.html", history=[])


@app.route("/medicine/search")
@login_required
def medicine_search():
    """Search medicines by name or generic name."""
    search_term = request.args.get("medicine", "").strip()
    medicines = []

    if search_term:
        connection = get_connection()
        medicines = connection.execute(
            """
            SELECT id, name, generic_name, category
            FROM medicines
            WHERE name LIKE ? OR generic_name LIKE ?
            ORDER BY name
            """,
            (f"%{search_term}%", f"%{search_term}%"),
        ).fetchall()
        connection.close()

    return render_template(
        "medicine_search.html",
        medicines=medicines,
        search_term=search_term,
    )


@app.route("/medicine/<int:medicine_id>")
@login_required
def medicine_details(medicine_id):
    """Display one medicine or a friendly not-found page."""
    connection = get_connection()
    medicine = connection.execute(
        "SELECT * FROM medicines WHERE id = ?",
        (medicine_id,),
    ).fetchone()
    connection.close()

    if medicine is None:
        return render_template("medicine_details.html", medicine=None), 404

    return render_template("medicine_details.html", medicine=medicine)


if __name__ == "__main__":
    app.run(debug=True)
