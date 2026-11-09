"""Pruebas de frontera contra la API usando los datos de data/frontera.py (Lab 3.2).

Una prueba que falla por un defecto real de la aplicación NO se modifica para que pase:
se reporta el defecto y la prueba se marca como fallo esperado (xfail) con la referencia.
"""
import pytest

from data import frontera

ADDRESS = {"street": "Calle 1", "neighborhood": "Centro", "city": "Monterrey", "state": "Nuevo León",
           "postal_code": "64000", "phone": "8112345678"}


def ids(casos):
    return [c[2] for c in casos]


# ---------- Área A · Cuentas ----------
@pytest.mark.parametrize("password,valido,desc", frontera.contrasenas(), ids=ids(frontera.contrasenas()))
def test_registro_contrasena(client, password, valido, desc):
    res = client.post("/api/auth/register", json={
        "name": "Cliente Prueba", "email": "frontera@example.com", "password": password,
        "password_confirm": password, "birth_date": "1990-01-01"})
    assert res.status_code == (201 if valido else 400)
    if not valido:
        assert "password" in res.json()["errors"]


@pytest.mark.parametrize("nacimiento,valido,desc", frontera.fechas_nacimiento(), ids=ids(frontera.fechas_nacimiento()))
def test_registro_mayoria_de_edad(client, nacimiento, valido, desc):
    res = client.post("/api/auth/register", json={
        "name": "Cliente Prueba", "email": "edad@example.com", "password": "Password123",
        "password_confirm": "Password123", "birth_date": nacimiento})
    assert res.status_code == (201 if valido else 400)


# ---------- Área C · Carrito ----------
CASOS_CANTIDAD = [
    pytest.param(*c, marks=pytest.mark.xfail(strict=True, reason="BUG-01: la API acepta 11 unidades (RN-05)"))
    if c[0] == 11 else c
    for c in frontera.cantidades()
]


@pytest.mark.parametrize("cantidad,valido,desc", CASOS_CANTIDAD, ids=ids(frontera.cantidades()))
def test_cantidad_en_carrito(auth_client, cantidad, valido, desc):
    # Producto 4 (Teclado Mecánico Kappa) tiene 35 unidades: el stock no interfiere
    res = auth_client.post("/api/cart/items", json={"product_id": 4, "quantity": cantidad})
    assert res.status_code == (200 if valido else 400)


# ---------- Área D · Checkout ----------
@pytest.mark.parametrize("cp,valido,desc", frontera.codigos_postales(), ids=ids(frontera.codigos_postales()))
def test_checkout_codigo_postal(auth_client, cp, valido, desc):
    auth_client.post("/api/cart/items", json={"product_id": 4, "quantity": 1})
    res = auth_client.post("/api/orders", json={"address": {**ADDRESS, "postal_code": cp}})
    assert res.status_code == (201 if valido else 400)


@pytest.mark.parametrize("tel,valido,desc", frontera.telefonos(), ids=ids(frontera.telefonos()))
def test_checkout_telefono(auth_client, tel, valido, desc):
    auth_client.post("/api/cart/items", json={"product_id": 4, "quantity": 1})
    res = auth_client.post("/api/orders", json={"address": {**ADDRESS, "phone": tel}})
    assert res.status_code == (201 if valido else 400)
