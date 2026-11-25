
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "users.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:

        # Store employee accounts.
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'employee',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
        """)

                # Add a role column to existing user databases.
        columns = connection.execute(
            "PRAGMA table_info(users)"
        ).fetchall()

        column_names = [column["name"] for column in columns]

        if "role" not in column_names:
            connection.execute("""
                ALTER TABLE users
                ADD COLUMN role TEXT NOT NULL DEFAULT 'employee'
            """)

        # Store IT support tickets.
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'General',
                priority TEXT NOT NULL DEFAULT 'Normal',
                status TEXT NOT NULL DEFAULT 'Open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
