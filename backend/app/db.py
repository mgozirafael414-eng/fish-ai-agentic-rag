import json
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bcrypt

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "fishai.sqlite3"
SESSION_DAYS = 30


class ManagedConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, factory=ManagedConnection)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                display_name TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS settings (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                dark_mode INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title TEXT NOT NULL DEFAULT 'New chat',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata_json TEXT,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_conversations_user_updated
                ON conversations(user_id, updated_at DESC);
            CREATE INDEX IF NOT EXISTS idx_messages_conversation_created
                ON messages(conversation_id, created_at ASC);
            """
        )


def create_user(email: str, password: str, display_name: str = "") -> dict:
    normalized_email = email.strip().lower()
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    now = _now()
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO users(email, password_hash, display_name, created_at) VALUES (?, ?, ?, ?)",
            (normalized_email, password_hash, display_name.strip(), now),
        )
        user_id = cursor.lastrowid
        connection.execute("INSERT INTO settings(user_id) VALUES (?)", (user_id,))
    return get_user(user_id)


def get_user(user_id: int) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, email, display_name, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def authenticate_user(email: str, password: str) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()
    if not row or not bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
        return None
    return get_user(row["id"])


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(40)
    expires_at = (datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)).isoformat()
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO sessions(token, user_id, expires_at, created_at) VALUES (?, ?, ?, ?)",
            (token, user_id, expires_at, _now()),
        )
    return token


def get_user_by_session(token: str) -> dict | None:
    if not token:
        return None
    with get_connection() as connection:
        row = connection.execute(
            "SELECT user_id, expires_at FROM sessions WHERE token = ?",
            (token,),
        ).fetchone()
    if not row:
        return None
    if datetime.fromisoformat(row["expires_at"]) <= datetime.now(timezone.utc):
        delete_session(token)
        return None
    return get_user(row["user_id"])


def delete_session(token: str) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM sessions WHERE token = ?", (token,))


def update_profile(user_id: int, display_name: str) -> dict | None:
    with get_connection() as connection:
        connection.execute(
            "UPDATE users SET display_name = ? WHERE id = ?",
            (display_name.strip(), user_id),
        )
    return get_user(user_id)


def get_settings(user_id: int) -> dict:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT dark_mode FROM settings WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if not row:
            connection.execute("INSERT INTO settings(user_id) VALUES (?)", (user_id,))
            return {"dark_mode": False}
    return {"dark_mode": bool(row["dark_mode"])}


def update_settings(user_id: int, dark_mode: bool) -> dict:
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO settings(user_id, dark_mode) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET dark_mode = excluded.dark_mode",
            (user_id, int(dark_mode)),
        )
    return get_settings(user_id)


def create_conversation(user_id: int, title: str = "New chat") -> dict:
    now = _now()
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO conversations(user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (user_id, title.strip() or "New chat", now, now),
        )
        conversation_id = cursor.lastrowid
    return get_conversation(user_id, conversation_id)


def get_conversations(user_id: int) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, title, created_at, updated_at FROM conversations "
            "WHERE user_id = ? ORDER BY updated_at DESC",
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_conversation(user_id: int, conversation_id: int) -> dict | None:
    with get_connection() as connection:
        conversation = connection.execute(
            "SELECT id, title, created_at, updated_at FROM conversations "
            "WHERE id = ? AND user_id = ?",
            (conversation_id, user_id),
        ).fetchone()
        if not conversation:
            return None
        messages = connection.execute(
            "SELECT id, role, content, metadata_json, created_at FROM messages "
            "WHERE conversation_id = ? AND user_id = ? ORDER BY id ASC",
            (conversation_id, user_id),
        ).fetchall()
    result = dict(conversation)
    result["messages"] = [
        {
            **dict(message),
            "metadata": json.loads(message["metadata_json"])
            if message["metadata_json"]
            else None,
        }
        for message in messages
    ]
    return result


def add_message(
    user_id: int,
    conversation_id: int,
    role: str,
    content: str,
    metadata: dict | None = None,
) -> dict:
    now = _now()
    with get_connection() as connection:
        owned = connection.execute(
            "SELECT id FROM conversations WHERE id = ? AND user_id = ?",
            (conversation_id, user_id),
        ).fetchone()
        if not owned:
            raise ValueError("Conversation not found")
        cursor = connection.execute(
            "INSERT INTO messages(conversation_id, user_id, role, content, metadata_json, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (conversation_id, user_id, role, content, json.dumps(metadata) if metadata else None, now),
        )
        connection.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ? AND user_id = ?",
            (now, conversation_id, user_id),
        )
        message_id = cursor.lastrowid
    return {"id": message_id, "role": role, "content": content, "metadata": metadata, "created_at": now}


def update_conversation_title(user_id: int, conversation_id: int, title: str) -> None:
    with get_connection() as connection:
        connection.execute(
            "UPDATE conversations SET title = ? WHERE id = ? AND user_id = ?",
            (title.strip() or "New chat", conversation_id, user_id),
        )


def delete_conversation(user_id: int, conversation_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM conversations WHERE id = ? AND user_id = ?",
            (conversation_id, user_id),
        )
    return cursor.rowcount > 0


init_db()
