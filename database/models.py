MEDICINES_TABLE = """
CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    generic_name TEXT NOT NULL,
    category TEXT NOT NULL,
    general_uses TEXT NOT NULL,
    warnings TEXT NOT NULL,
    side_effects TEXT NOT NULL,
    ingredients TEXT NOT NULL DEFAULT '',
    storage_information TEXT NOT NULL,
    interaction_information TEXT NOT NULL,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

CHAT_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    medicine_id INTEGER,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    intent TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'USER',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


DEMO_MEDICINES = [
    {
        "name": "Paracetamol",
        "generic_name": "Paracetamol",
        "category": "Pain reliever and fever reducer",
        "general_uses": "Demo information: commonly used for pain and fever. Follow the product label and ask a healthcare professional for advice.",
        "warnings": "Demo information: do not use more than the label allows. Ask a healthcare professional if you have questions or other health conditions.",
        "side_effects": "Demo information: medicines can cause side effects. Read the package leaflet and seek professional advice if you are concerned.",
        "ingredients": "Paracetamol",
        "storage_information": "Store according to the package instructions and keep out of the reach of children.",
        "interaction_information": "Check the package leaflet or ask a pharmacist before combining this medicine with other medicines.",
        "source": "Demo record. Reference: NHS, Paracetamol for adults - https://www.nhs.uk/medicines/paracetamol-for-adults/",
    },
    {
        "name": "Ibuprofen",
        "generic_name": "Ibuprofen",
        "category": "Non-steroidal anti-inflammatory medicine",
        "general_uses": "Demo information: commonly used for some types of pain and inflammation. Follow the product label and ask a healthcare professional for advice.",
        "warnings": "Demo information: ask a healthcare professional whether this medicine is suitable for you, especially if you have other health conditions.",
        "side_effects": "Demo information: medicines can cause side effects. Read the package leaflet and seek professional advice if you are concerned.",
        "ingredients": "Ibuprofen",
        "storage_information": "Store according to the package instructions and keep out of the reach of children.",
        "interaction_information": "Check the package leaflet or ask a pharmacist before combining this medicine with other medicines.",
        "source": "Demo record. Reference: NHS, Ibuprofen for adults - https://www.nhs.uk/medicines/ibuprofen-for-adults/",
    },
]
