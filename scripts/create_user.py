
import getpass
import sys
import sqlite3
from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import HashingError

# Allow imports from the backend package.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database import get_connection, initialize_database

password_hasher = PasswordHasher()


def create_user():
    initialize_database()

    username = input("Enter username: ").strip()

    if not username:
        print("Username cannot be empty.")
        return

    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if len(password) < 12:
        print("Password must be at least 12 characters.")
        return

    if password != confirm_password:
        print("Passwords do not match.")
        return

    try:
        password_hash = password_hasher.hash(password)

        with get_connection() as connection:
            connection.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )

        print(f"Account '{username}' created successfully!")

    except sqlite3.IntegrityError:
        print("That username already exists.")

    except HashingError:
        print("Could not securely hash the password.")


if __name__ == "__main__":
    create_user()
