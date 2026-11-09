"""Pruebas de frontera contra la API usando los datos de data/frontera.py (Lab 3.2).

Fixtures disponibles (tests/conftest.py):
- client: cliente de la API con la base de datos reiniciada
- auth_client: lo mismo, con sesión iniciada como Ana García

Una prueba que falla por un defecto real de la aplicación NO se modifica para que pase:
se reporta el defecto en integradora/defectos.md y la prueba se marca como fallo esperado:
    pytest.param(..., marks=pytest.mark.xfail(strict=True, reason="BUG-01: descripción"))
"""
import pytest

from data import frontera


def ids(casos):
    return [c[2] for c in casos]


# ---------- Ejemplo · Área A · RN-02 ----------
@pytest.mark.parametrize("password,valido,desc", frontera.contrasenas(), ids=ids(frontera.contrasenas()))
def test_registro_contrasena(client, password, valido, desc):
    res = client.post("/api/auth/register", json={
        "name": "Cliente Prueba", "email": "frontera@example.com", "password": password,
        "password_confirm": password, "birth_date": "1990-01-01"})
    assert res.status_code == (201 if valido else 400)
    if not valido:
        assert "password" in res.json()["errors"]


# TODO: agreguen aquí las pruebas de su área, una función de prueba por regla.
