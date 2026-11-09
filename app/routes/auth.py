"""HU-01 Registro y HU-02 Inicio de sesión."""
import json
import re
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.db import get_db
from app.schemas import AuthOut, ErrorOut, LoginIn, RegisterIn, UserOut
from app.security import (LOCK_DURATION, MAX_FAILED_ATTEMPTS, create_session, current_user,
                          hash_password, now, verify_password)

router = APIRouter(prefix="/api", tags=["auth"])

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")


def user_out(user) -> dict:
    address = json.loads(user["saved_address"]) if user["saved_address"] else None
    return {"id": user["id"], "name": user["name"], "email": user["email"], "saved_address": address}


def age_on(birth: date, today: date) -> int:
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


@router.post("/auth/register", response_model=AuthOut, status_code=201,
             responses={400: {"model": ErrorOut}, 409: {"model": ErrorOut}})
def register(data: RegisterIn, conn=Depends(get_db)):
    errors = {}
    if not data.name.strip():
        errors["name"] = "El nombre es obligatorio"
    if not data.email.strip():
        errors["email"] = "El correo es obligatorio"
    elif not EMAIL_RE.match(data.email.strip()):
        errors["email"] = "El correo no tiene un formato válido"
    pwd = data.password
    if not pwd:
        errors["password"] = "La contraseña es obligatoria"
    elif not (8 <= len(pwd) <= 64) or not re.search(r"[A-Za-z]", pwd) or not re.search(r"\d", pwd):
        errors["password"] = "La contraseña debe tener entre 8 y 64 caracteres, con al menos una letra y un número"
    if pwd and data.password_confirm != pwd:
        errors["password_confirm"] = "Las contraseñas no coinciden"
    try:
        birth = date.fromisoformat(data.birth_date)
        if age_on(birth, date.today()) < 18:
            errors["birth_date"] = "Debes ser mayor de edad para registrarte"
    except ValueError:
        errors["birth_date"] = "La fecha de nacimiento es obligatoria (AAAA-MM-DD)"
    if errors:
        return JSONResponse(status_code=400, content={"detail": "Revisa los datos del formulario", "errors": errors})

    email = data.email.strip()
    if conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
        return JSONResponse(status_code=409, content={"detail": "Revisa los datos del formulario",
                                                      "errors": {"email": "Este correo ya está registrado"}})
    cur = conn.execute(
        "INSERT INTO users (name, email, password_hash, birth_date, created_at) VALUES (?, ?, ?, ?, ?)",
        (data.name.strip(), email, hash_password(pwd), data.birth_date, now().isoformat()))
    user = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    return {"token": create_session(conn, user["id"]), "user": user_out(user)}


@router.post("/auth/login", response_model=AuthOut, responses={401: {"model": ErrorOut}, 423: {"model": ErrorOut}})
def login(data: LoginIn, conn=Depends(get_db)):
    generic = HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    user = conn.execute("SELECT * FROM users WHERE email = ?", (data.email.strip(),)).fetchone()
    if user is None:
        raise HTTPException(status_code=404, detail="Correo o contraseña incorrectos")
    if user["locked_until"] and datetime.fromisoformat(user["locked_until"]) > now():
        raise HTTPException(status_code=423, detail="Cuenta bloqueada temporalmente. Intenta más tarde.")
    if not verify_password(data.password, user["password_hash"]):
        attempts = user["failed_attempts"] + 1
        if attempts >= MAX_FAILED_ATTEMPTS:
            conn.execute("UPDATE users SET failed_attempts = 0, locked_until = ? WHERE id = ?",
                         ((now() + LOCK_DURATION).isoformat(), user["id"]))
        else:
            conn.execute("UPDATE users SET failed_attempts = ? WHERE id = ?", (attempts, user["id"]))
        conn.commit()
        raise generic
    conn.execute("UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE id = ?", (user["id"],))
    return {"token": create_session(conn, user["id"]), "user": user_out(user)}


@router.post("/auth/logout", status_code=204)
def logout(auth=Depends(current_user), conn=Depends(get_db)):
    conn.execute("DELETE FROM sessions WHERE token = ?", (auth["token"],))


@router.get("/me", response_model=UserOut, responses={401: {"model": ErrorOut}})
def me(auth=Depends(current_user)):
    return user_out(auth["user"])
