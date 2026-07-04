"""
auth.py
Simple username/password authentication backed by the users table.
Passwords are hashed with bcrypt before storage.
Works for a single user (just register one account) or many users
(each person registers their own account and only ever sees their own data).
"""

import bcrypt
from database import get_connection


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def register_user(username: str, password: str, full_name: str = ""):
    """Create a new user. Returns (success: bool, message: str)."""
    username = username.strip().lower()
    if not username or not password:
        return False, "Username and password are required."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cur.fetchone():
        conn.close()
        return False, "That username is already taken."

    cur.execute(
        "INSERT INTO users (username, password_hash, full_name) VALUES (?, ?, ?)",
        (username, hash_password(password), full_name.strip()),
    )
    conn.commit()
    conn.close()
    return True, "Account created. You can now log in."


def authenticate_user(username: str, password: str):
    """Returns the user row (dict) on success, or None on failure."""
    username = username.strip().lower()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row and verify_password(password, row["password_hash"]):
        return dict(row)
    return None


def any_users_exist() -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM users")
    count = cur.fetchone()["c"]
    conn.close()
    return count > 0
