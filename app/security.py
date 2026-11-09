"""Contraseñas, sesiones y autenticación."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

from fastapi import Depends, Header, HTTPException

from app.db import get_db

SESSION_TIMEOUT = timedelta(minutes=30)
MAX_FAILED_ATTEMPTS = 5
LOCK_DURATION = timedelta(minutes=15)


def now() -> datetime:
    return datetime.now()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    salt, digest = stored.split("$", 1)
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return hmac.compare_digest(candidate, digest)


def create_session(conn, user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    conn.execute("INSERT INTO sessions (token, user_id, last_seen) VALUES (?, ?, ?)",
                 (token, user_id, now().isoformat()))
    return token


def current_user(authorization: str | None = Header(default=None), conn=Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Debes iniciar sesión")
    token = authorization.removeprefix("Bearer ").strip()
    session = conn.execute("SELECT * FROM sessions WHERE token = ?", (token,)).fetchone()
    if session is None:
        raise HTTPException(status_code=401, detail="Debes iniciar sesión")
    if now() - datetime.fromisoformat(session["last_seen"]) > SESSION_TIMEOUT:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        raise HTTPException(status_code=401, detail="Tu sesión expiró")
    conn.execute("UPDATE sessions SET last_seen = ? WHERE token = ?", (now().isoformat(), token))
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    return {"user": user, "token": token}
