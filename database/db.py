import sqlite3
from pathlib import Path

from .models import CHAT_HISTORY_TABLE, DEMO_MEDICINES, MEDICINES_TABLE, USERS_TABLE


DATABASE_PATH = Path(__file__).resolve().parent.parent / "database.db"


def get_connection():
    """Create a SQLite connection for the project database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    """Create the medicines table and add missing demo records."""
    connection = get_connection()
    connection.execute(MEDICINES_TABLE)
    connection.execute(USERS_TABLE)
    connection.execute(CHAT_HISTORY_TABLE)
    history_columns = [
        row["name"] for row in connection.execute("PRAGMA table_info(chat_history)")
    ]
    if "user_id" not in history_columns:
        connection.execute("ALTER TABLE chat_history ADD COLUMN user_id INTEGER")
    medicine_columns = [
        row["name"] for row in connection.execute("PRAGMA table_info(medicines)")
    ]
    if "ingredients" not in medicine_columns:
        connection.execute(
            "ALTER TABLE medicines ADD COLUMN ingredients TEXT NOT NULL DEFAULT ''"
        )
    connection.executemany(
        """
        INSERT OR IGNORE INTO medicines (
            name, generic_name, category, general_uses, warnings,
            side_effects, ingredients, storage_information, interaction_information, source
        ) VALUES (
            :name, :generic_name, :category, :general_uses, :warnings,
            :side_effects, :ingredients, :storage_information, :interaction_information, :source
        )
        """,
        DEMO_MEDICINES,
    )
    connection.executemany(
        "UPDATE medicines SET ingredients = :ingredients WHERE name = :name AND ingredients = ''",
        DEMO_MEDICINES,
    )
    connection.commit()
    connection.close()
