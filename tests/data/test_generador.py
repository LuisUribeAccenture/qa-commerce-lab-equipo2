"""Pruebas del generador de datos sintéticos (Lab 3.1). Deben pasar todas."""
import re
from datetime import date

from data.generador import (CATEGORIAS, FECHA_REFERENCIA, cargar_en_app, generar_clientes, generar_dataset,
                            generar_productos)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")


def edad(nacimiento: str, ref: date) -> int:
    n = date.fromisoformat(nacimiento)
    return ref.year - n.year - ((ref.month, ref.day) < (n.month, n.day))


# ---------- Reproducibilidad ----------
def test_misma_semilla_mismo_resultado():
    assert generar_dataset(seed=7) == generar_dataset(seed=7)


def test_distinta_semilla_distinto_resultado():
    assert generar_dataset(seed=7) != generar_dataset(seed=8)


# ---------- Clientes ----------
def test_cantidad_de_clientes():
    assert len(generar_clientes(25)) == 25


def test_correos_validos_unicos_y_ficticios():
    clientes = generar_clientes(200)
    correos = [c["email"] for c in clientes]
    assert all(EMAIL_RE.match(e) for e in correos)
    assert len(set(correos)) == len(correos)
    assert all(e.endswith("@example.com") for e in correos)
    assert all(e.isascii() for e in correos)


def test_contrasenas_cumplen_rn02():
    for c in generar_clientes(200):
        p = c["password"]
        assert 8 <= len(p) <= 64
        assert re.search(r"[A-Za-z]", p) and re.search(r"\d", p)


def test_clientes_mayores_de_edad_rn03():
    for c in generar_clientes(200):
        assert edad(c["birth_date"], FECHA_REFERENCIA) >= 18


# ---------- Productos ----------
def test_productos_con_datos_validos():
    for p in generar_productos(200):
        assert p["category"] in CATEGORIAS
        assert p["price"] > 0 and round(p["price"], 2) == p["price"]
        assert p["stock"] >= 0
        assert p["name"].strip()


def test_productos_cubren_casos_de_stock():
    stocks = {p["stock"] for p in generar_productos(200)}
    assert 0 in stocks  # agotado
    assert any(1 <= s <= 5 for s in stocks)  # últimas unidades
    assert any(s > 5 for s in stocks)


# ---------- Integración con la app ----------
def test_el_dataset_se_carga_en_la_app(client):
    dataset = generar_dataset(seed=3, clientes=3, productos=4)
    creados = cargar_en_app(dataset, client)
    assert len(creados["users"]) == 3 and len(creados["products"]) == 4

    cliente = dataset["users"][0]
    login = client.post("/api/auth/login", json={"email": cliente["email"], "password": cliente["password"]})
    assert login.status_code == 200
