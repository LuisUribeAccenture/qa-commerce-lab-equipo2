"""Lab 6.2 · Respuestas simuladas de la API y comportamiento real del catálogo."""

import re

import pytest
from jsonschema import Draft202012Validator
from playwright.sync_api import Page, expect


PRODUCTOS = re.compile(r"/api/products(?:\?.*)?$")
CATALOGO_VACIO = {"items": [], "total": 0, "page": 1, "page_size": 20}
PRODUCTO_AGOTADO = {
    "id": 601,
    "name": "Taza sintética",
    "description": "Producto de prueba para el catálogo",
    "price": 120.0,
    "category": "Hogar",
    "category_id": 4,
    "stock": 0,
    "available": False,
    "low_stock": False,
    "image": "/static/img/4.svg",
}
CATALOGO_AGOTADO = {**CATALOGO_VACIO, "items": [PRODUCTO_AGOTADO], "total": 1}


def test_catalogo_con_error_del_servidor(page: Page):  # ejemplo
    page.route("**/api/products*", lambda route: route.fulfill(
        status=503, json={"detail": "Servicio no disponible"}))

    page.goto("/")

    expect(page.locator("#flash")).to_have_text("Servicio no disponible")


def test_catalogo_vacio_muestra_mensaje_y_ninguna_tarjeta(page: Page):
    # CA-04.5 · Sin resultados, la interfaz informa al visitante.
    page.route(PRODUCTOS, lambda route: route.fulfill(status=200, json=CATALOGO_VACIO))
    page.goto("/?search=producto-sintetico-inexistente")

    expect(page.get_by_text("No encontramos productos para tu búsqueda", exact=True)).to_be_visible()
    expect(page.get_by_role("region", name="Productos").get_by_role("article")).to_have_count(0)


def test_producto_agotado_muestra_etiqueta_y_desactiva_agregar(page: Page):
    # CA-03.3 · El catálogo indica que el producto está agotado e impide agregarlo.
    page.route(PRODUCTOS, lambda route: route.fulfill(status=200, json=CATALOGO_AGOTADO))
    page.goto("/")

    nombre = PRODUCTO_AGOTADO["name"]
    tarjeta = page.get_by_role("article").filter(
        has=page.get_by_role("link", name=nombre, exact=True),
    )
    expect(tarjeta.get_by_text("Agotado", exact=True)).to_be_visible()
    expect(tarjeta.get_by_role("button", name=f"Agregar {nombre} al carrito", exact=True)).to_be_disabled()


@pytest.mark.parametrize("respuesta", [CATALOGO_VACIO, CATALOGO_AGOTADO], ids=["vacio", "agotado"])
def test_el_mock_cumple_el_contrato(client, respuesta):
    contrato = client.get("/openapi.json")
    assert contrato.status_code == 200
    esquema = {"$ref": "#/components/schemas/ProductPage", "components": contrato.json()["components"]}
    Draft202012Validator(esquema).validate(respuesta)
