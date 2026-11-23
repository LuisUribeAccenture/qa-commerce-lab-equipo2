"""Pruebas de frontera contra la API usando los datos de data/frontera.py (Lab 3.2).

Fixtures disponibles (tests/conftest.py):
- client: cliente de la API con la base de datos reiniciada
- auth_client: lo mismo, con sesión iniciada como Ana García

Una prueba que falla por un defecto real de la aplicación NO se modifica para que pase:
se reporta el defecto en integradora/defectos.md y la prueba se marca como fallo esperado:
    pytest.param(..., marks=pytest.mark.xfail(strict=True, reason="BUG-01: descripción"))
"""
from datetime import date

import pytest

from app.routes import auth
from data import frontera
from data.generador import FECHA_REFERENCIA, cargar_en_app, generar_invalidos


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


# ---------- Área B · Catálogo ----------
@pytest.mark.parametrize("caso,valida,desc", frontera.paginas(), ids=ids(frontera.paginas()))
def test_paginacion_catalogo(client, caso, valida, desc):
    total, pagina_inicial, tamanios = caso
    prefijo = "Catálogo Frontera B"
    productos = [{"name": f"{prefijo} {i + 1}", "price": 100} for i in range(total)]
    productos.append({"name": f"{prefijo} inactivo", "price": 100, "active": False})
    creados = cargar_en_app({"products": productos}, client)["products"]

    if not valida:
        res = client.get("/api/products", params={"search": prefijo, "page": pagina_inicial})
        assert res.status_code == 422
        assert res.json()["detail"][0]["loc"] == ["query", "page"]
        return

    vistos = []
    for pagina, tamanio in enumerate(tamanios, start=pagina_inicial):
        res = client.get("/api/products", params={
            "search": prefijo, "page": pagina, "sort": "price_asc",
        })
        assert res.status_code == 200
        datos = res.json()
        assert (datos["page"], datos["page_size"], datos["total"]) == (pagina, 20, total)
        assert len(datos["items"]) == tamanio
        vistos.extend(producto["id"] for producto in datos["items"])

    assert sorted(vistos) == sorted(creados[:-1])


casos_existencias = [
    pytest.param(
        stock, aviso, desc,
        marks=pytest.mark.xfail(strict=True, reason="BUG-01: CA-05.2 incluye el stock 0"),
    ) if stock == 0 else (stock, aviso, desc)
    for stock, aviso, desc in frontera.existencias()
]


@pytest.mark.parametrize("stock,aviso,desc", casos_existencias, ids=ids(frontera.existencias()))
def test_detalle_ultimas_unidades(client, stock, aviso, desc):
    creado = cargar_en_app({"products": [{
        "name": "Taza Frontera B", "price": 100, "stock": stock,
    }]}, client)["products"][0]

    res = client.get(f"/api/products/{creado}")

    assert res.status_code == 200
    datos = res.json()
    assert datos["stock"] == stock
    assert datos["low_stock"] is aviso


@pytest.mark.parametrize("consulta,coincide,desc", frontera.busquedas(), ids=ids(frontera.busquedas()))
def test_busqueda_por_nombre(client, consulta, coincide, desc):
    creado = cargar_en_app({"products": [{
        "name": "Taza Frontera B", "description": "Cerámica Frontera B", "price": 100,
    }]}, client)["products"][0]

    res = client.get("/api/products", params={"search": consulta})

    assert res.status_code == 200
    datos = res.json()
    assert [producto["id"] for producto in datos["items"]] == ([creado] if coincide else [])
    assert datos["total"] == int(coincide)


# ---------- Desafío · Clientes inválidos ----------
class FechaDeRegistro(date):
    @classmethod
    def today(cls):
        return FECHA_REFERENCIA


@pytest.mark.parametrize(
    "campo,datos",
    zip(("password", "birth_date", "email"), generar_invalidos(seed=42)),
    ids=("sin-numero", "menor-de-edad", "correo-mal-formado"),
)
def test_registro_rechaza_clientes_invalidos(client, monkeypatch, campo, datos):
    monkeypatch.setattr(auth, "date", FechaDeRegistro)
    solicitud = {**datos, "password_confirm": datos["password"]}

    res = client.post("/api/auth/register", json=solicitud)

    assert res.status_code == 400
    assert set(res.json()["errors"]) == {campo}
    assert "token" not in res.json()
