"""Create or update a development ADMIN account from environment variables."""

import os
import sys

from werkzeug.security import generate_password_hash

from database.db import get_connection, init_database


email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
password = os.environ.get("ADMIN_PASSWORD", "")
name = os.environ.get("ADMIN_NAME", "Development Admin").strip()

if not email or not password:
    print("Set ADMIN_EMAIL and ADMIN_PASSWORD before running this command.")
    sys.exit(1)

init_database()
connection = get_connection()
existing_user = connection.execute(
    "SELECT id FROM users WHERE email = ?", (email,)
).fetchone()

if existing_user:
    connection.execute(
        "UPDATE users SET name = ?, password_hash = ?, role = 'ADMIN' WHERE id = ?",
        (name, generate_password_hash(password), existing_user["id"]),
    )
else:
    connection.execute(
        "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, 'ADMIN')",
        (name, email, generate_password_hash(password)),
    )

connection.commit()
connection.close()
print(f"Development admin account ready for {email}.")
