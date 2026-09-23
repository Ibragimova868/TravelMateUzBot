"""
Database management module for Sayohatchi Telegram Bot.
Handles SQLite connection, schema creation, and parameterized CRUD operations.
"""

import sqlite3
import logging
from typing import Optional, Dict, Any
from config import DATABASE_PATH

logger = logging.getLogger(__name__)


def get_db_connection() -> sqlite3.Connection:
    """Creates and returns a connection to the SQLite database with Row factory."""
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Initializes the SQLite database schema automatically if it does not already exist.
    Creates the 'users' table with all required fields.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    language TEXT NOT NULL DEFAULT 'uz',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            # Create an index on telegram_id if not automatically done
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id)
                """
            )
            conn.commit()
            logger.info("Database initialized successfully at: %s", DATABASE_PATH)
    except sqlite3.Error as e:
        logger.error("Database initialization failed: %s", e)
        raise


def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetches user record by telegram_id.
    Returns a dict with user fields or None if not found.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT telegram_id, first_name, last_name, language, created_at
                FROM users
                WHERE telegram_id = ?
                """,
                (telegram_id,),
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    except sqlite3.Error as e:
        logger.error("Error fetching user %s: %s", telegram_id, e)
        return None


def create_user(
    telegram_id: int, first_name: str, last_name: str, language: str = "uz"
) -> bool:
    """
    Inserts or updates a user in the database using parameterized query.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (telegram_id, first_name, last_name, language)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET
                    first_name = excluded.first_name,
                    last_name = excluded.last_name,
                    language = excluded.language
                """,
                (telegram_id, first_name.strip(), last_name.strip(), language.strip()),
            )
            conn.commit()
            logger.info("User %s created/updated successfully.", telegram_id)
            return True
    except sqlite3.Error as e:
        logger.error("Error creating user %s: %s", telegram_id, e)
        return False


def update_user_language(telegram_id: int, language: str) -> bool:
    """Updates user's preferred language."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE users
                SET language = ?
                WHERE telegram_id = ?
                """,
                (language.strip(), telegram_id),
            )
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error("Error updating language for user %s: %s", telegram_id, e)
        return False


def update_user_name(telegram_id: int, first_name: str, last_name: str) -> bool:
    """Updates user's first and last name."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE users
                SET first_name = ?, last_name = ?
                WHERE telegram_id = ?
                """,
                (first_name.strip(), last_name.strip(), telegram_id),
            )
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error("Error updating name for user %s: %s", telegram_id, e)
        return False


def get_user_language(telegram_id: int) -> str:
    """
    Convenience function to get user language, defaulting to 'uz' if not registered.
    """
    user = get_user(telegram_id)
    if user and user.get("language"):
        return user["language"]
    return "uz"
