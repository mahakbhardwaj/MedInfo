# MedInfo

MedInfo is an AI-powered medicine information assistant developed as a B.Tech final-year project. It provides authenticated users with a focused interface for searching medicine records, viewing medicine details, asking medicine-related questions, scanning medicine package images, and reviewing saved chatbot conversations.

The application combines a Flask web interface with a SQLite database, an optional OpenAI-powered response layer, and Tesseract OCR for reading medicine package text.

## Project Overview

MedInfo is designed to make general medicine information easier to access in one place. Users can search the application's medicine database, inspect available information, ask questions through the chatbot, and use OCR-based scanning to identify a medicine from an uploaded image.

The project also includes role-based administration features for maintaining medicine records and viewing basic usage statistics.

## Features

1. User registration and login
2. Medicine search by medicine name or generic name
3. Medicine details including uses, warnings, side effects, ingredients, storage, interactions, and source information
4. AI chatbot for medicine-related questions
5. OCR-based medicine image scanning
6. Medicine name detection from scanned images
7. User-specific chat history
8. Admin dashboard with basic statistics
9. Medicine database management, including adding, editing, and deleting records
10. Safety and medical disclaimer messaging

## Technology Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **AI integration:** OpenAI API
- **OCR:** Tesseract OCR through `pytesseract`
- **Image processing:** Pillow
- **Authentication and security utilities:** Werkzeug
- **Configuration:** `python-dotenv`
- **Frontend:** HTML, CSS, JavaScript

## How It Works

1. A user registers or logs in to the application.
2. Flask manages requests, sessions, authentication checks, and page rendering.
3. Medicine information is read from the SQLite database.
4. Search results link to individual medicine detail pages.
5. The chatbot uses the selected medicine record and the user's question to produce a database-backed answer. When a valid OpenAI configuration is available, the optional OpenAI integration can generate the response; otherwise, the local chatbot behavior remains available.
6. For scanning, the user uploads a supported PNG, JPG, JPEG, or WEBP image.
7. Tesseract OCR extracts text from the image, and MedInfo compares the detected text with medicine names and generic names in the database.
8. Chatbot questions and responses are stored in the logged-in user's chat history.
9. Administrators can manage medicine records and view basic counts for medicines, users, and conversations.

## Project Structure

```text
MedInfo/
├── app.py                         # Flask application and routes
├── create_admin.py                # Development admin account setup
├── requirements.txt               # Python dependencies
├── database.db                    # SQLite database
├── REVIEW_DB_UPDATE.txt           # Review-only database update script
├── ai/
│   ├── __init__.py
│   └── llm.py                     # Optional OpenAI integration
├── chatbot/
│   ├── __init__.py
│   ├── chatbot.py                 # Chatbot response handling
│   └── intents.py                 # Supported chatbot intents
├── database/
│   ├── __init__.py
│   ├── db.py                      # SQLite connection and initialization
│   └── models.py                  # Table definitions and demo records
├── ocr/
│   ├── __init__.py
│   └── ocr.py                     # OCR and medicine identification
├── static/
│   ├── css/style.css              # Application styles
│   └── js/script.js               # Client-side behavior
└── templates/                     # Jinja2 page templates
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── medicine_search.html
    ├── medicine_details.html
    ├── scan.html
    ├── chatbot.html
    ├── history.html
    └── admin/
        ├── dashboard.html
        ├── medicines.html
        ├── medicine_form.html
        ├── users.html
        └── chat_statistics.html
```

## Installation and Setup

### 1. Clone or open the project

Open the existing MedInfo project directory in a terminal.

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file in the project root when these settings are needed. Do not commit the file or expose its values.

### 5. Configure OCR

Install Tesseract OCR as described in the [OCR Setup](#ocr-setup) section.

### 6. Create an administrator account, if required

Set the administrator variables and run:

```powershell
python create_admin.py
```

The script creates or updates the account using the configured administrator email and password.

## Environment Variables

The application reads the following variables:

| Variable | Purpose | Required |
|---|---|---|
| `OPENAI_API_KEY` | Enables the optional OpenAI chatbot integration | Optional |
| `AI_MODEL` | OpenAI model name; defaults to `gpt-4o-mini` | Optional |
| `SECRET_KEY` | Flask session signing key | Recommended |
| `ADMIN_EMAIL` | Administrator email used by `create_admin.py` | Required for admin setup |
| `ADMIN_PASSWORD` | Administrator password used by `create_admin.py` | Required for admin setup |
| `ADMIN_NAME` | Administrator display name | Optional |

Example `.env` structure with placeholder values only:

```dotenv
SECRET_KEY=replace-with-a-long-random-value
OPENAI_API_KEY=replace-with-your-own-key
AI_MODEL=gpt-4o-mini
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=replace-with-a-strong-password
ADMIN_NAME=Development Admin
```

Never place a real API key, password, or production secret in this README or in source control.

## How to Run

Activate the virtual environment and start the Flask application:

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

The application runs in Flask debug mode using the development server. Open the local address shown in the terminal, typically:

```text
http://127.0.0.1:5000/
```

## OCR Setup

MedInfo uses Tesseract OCR through `pytesseract`. On Windows:

1. Install Tesseract OCR on the machine.
2. Ensure the Tesseract executable is available at:

   ```text
   C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

3. If Tesseract is installed elsewhere, update the configured executable path in `ocr/ocr.py` before using image scanning.
4. Upload a clear PNG, JPG, JPEG, or WEBP image of a medicine package.

The application validates the uploaded image, extracts visible text, and checks it against medicine names and generic names stored in the SQLite database.

## Example Use Cases

- A student searches for a medicine and reviews its general uses and warnings.
- A user opens a medicine detail page to check storage and interaction information available in the database.
- A user asks the chatbot a general question about a medicine record.
- A user uploads a medicine package image to detect its name and find a matching database record.
- A logged-in user reviews previously saved chatbot conversations.
- An administrator adds a new medicine record or updates existing medicine information.
- An administrator reviews the available medicine, user, and conversation counts.

## Safety Disclaimer

MedInfo provides general medicine information for educational purposes only. It does not provide medical diagnosis or treatment advice. Chatbot responses are not a substitute for professional medical care and must not be used to decide whether to start, stop, or change medication.

For personal medical questions, medicine interactions, urgent symptoms, or treatment decisions, consult a qualified doctor or pharmacist.

## Future Enhancements

- Improve medicine recognition for a broader range of package layouts and image conditions.
- Expand the medicine database with additional verified records and references.
- Add stronger production deployment and secret-management configuration.
- Add more detailed analytics and filtering to the admin dashboard.
- Improve automated testing coverage for search, chatbot, authentication, and OCR workflows.
- Add accessibility and localization improvements as the project grows.

## Author

**Project Author:** *Add project author name here*

B.Tech Final-Year Project
