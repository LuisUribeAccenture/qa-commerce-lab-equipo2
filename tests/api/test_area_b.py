"""Pruebas de contrato del área B · Catálogo (HU-03, HU-04 y HU-05)."""

import pytest

from tests.api.contrato import validar


def test_categorias_del_catalogo(api, contrato):
    """docs/requisitos.md §4.1 y OpenAPI GET /api/categories → 200."""
    respuesta = api.get("/api/categories")

    assert respuesta.status_code == 200
    categorias = respuesta.json()
    assert isinstance(categorias, list)
    for categoria in categorias:
        validar(contrato, "Category", categoria)

    assert sorted(categoria["name"] for categoria in categorias) == [
        "Accesorios", "Audio", "Computación", "Hogar", "Telefonía",
    ]


def test_paginas_del_catalogo_no_repiten_productos(api, contrato):
    """docs/requisitos.md CA-03.2 · El catálogo se pagina en grupos de 20."""
    # app/seed.py contiene 38 productos activos y dos inactivos (CA-03.4).
    total_esperado = 38
    paginas = []
    for numero, cantidad_esperada in ((1, 20), (2, 18)):
        respuesta = api.get("/api/products", params={"page": numero})

        assert respuesta.status_code == 200
        pagina = respuesta.json()
        validar(contrato, "ProductPage", pagina)
        assert pagina["page"] == numero
        assert pagina["page_size"] == 20
        assert pagina["total"] == total_esperado
        assert len(pagina["items"]) == cantidad_esperada
        paginas.append(pagina)

    ids = {producto["id"] for pagina in paginas for producto in pagina["items"]}
    assert len(ids) == total_esperado


@pytest.mark.parametrize(
    ("orden", "productos_esperados"),
    [
        ("price_asc", [("Laptop Nébula 14", 18_999.00), ("Laptop Titán 16", 32_499.00)]),
        ("price_desc", [("Laptop Titán 16", 32_499.00), ("Laptop Nébula 14", 18_999.00)]),
    ],
)
def test_busqueda_combina_nombre_categoria_y_orden(api, contrato, orden, productos_esperados):
    """docs/requisitos.md CA-03.4 y CA-04.1 a CA-04.4 · Coincidencias según app/seed.py."""
    respuesta = api.get("/api/products", params={"search": "Laptop", "category": 1, "sort": orden})

    assert respuesta.status_code == 200
    pagina = respuesta.json()
    validar(contrato, "ProductPage", pagina)
    assert pagina["total"] == len(productos_esperados)
    assert [(producto["name"], producto["price"]) for producto in pagina["items"]] == productos_esperados
    assert all(producto["category"] == "Computación" for producto in pagina["items"])


@pytest.mark.parametrize(
    "busqueda",
    [
        pytest.param("producto-qacl-no-existe", id="sin-coincidencias"),
        pytest.param("Laptop Nébula 13 (2023)", id="producto-inactivo"),
    ],
)
def test_busqueda_sin_productos_visibles(api, contrato, busqueda):
    """docs/requisitos.md CA-03.4 y CA-04.5 · La API entrega una página vacía."""
    respuesta = api.get("/api/products", params={"search": busqueda})

    assert respuesta.status_code == 200
    pagina = respuesta.json()
    validar(contrato, "ProductPage", pagina)
    assert pagina["total"] == 0
    assert pagina["items"] == []


@pytest.mark.parametrize(
    ("parametro", "valor"), [("page", 0), ("sort", "name")],
)
def test_catalogo_rechaza_parametros_fuera_del_contrato(api, contrato, parametro, valor):
    """OpenAPI GET /api/products · page tiene mínimo 1 y sort tiene un enum de precios."""
    respuesta = api.get("/api/products", params={parametro: valor})

    assert respuesta.status_code == 422
    error = respuesta.json()
    validar(contrato, "HTTPValidationError", error)
    assert ["query", parametro] in [detalle["loc"] for detalle in error["detail"]]


@pytest.mark.parametrize(
    ("producto_id", "nombre", "stock", "disponible", "ultimas_unidades"),
    [
        (6, "Disco SSD Externo 1 TB", 0, False, False),
        (14, "Tocadiscos Retro", 5, True, True),
        (24, "Aspiradora Robot Clean", 6, True, False),
    ],
)
def test_detalle_informa_disponibilidad_y_stock_bajo(
    api, contrato, producto_id, nombre, stock, disponible, ultimas_unidades,
):
    """docs/requisitos.md CA-03.3, CA-05.1 y CA-05.2 · Existencias según app/seed.py."""
    respuesta = api.get(f"/api/products/{producto_id}")

    assert respuesta.status_code == 200
    producto = respuesta.json()
    validar(contrato, "ProductOut", producto)
    assert producto["id"] == producto_id
    assert producto["name"] == nombre
    assert producto["stock"] == stock
    assert producto["available"] is disponible
    assert producto["low_stock"] is ultimas_unidades


def test_consultar_catalogo_no_descuenta_existencias(api, contrato):
    """CA-05.1 consulta existencias. CA-11.4 describe el descuento al pagar."""
    ruta_detalle = "/api/products/4"
    detalle_inicial = api.get(ruta_detalle)
    listado = api.get("/api/products", params={"search": "Teclado Mecánico Kappa"})
    detalle_final = api.get(ruta_detalle)

    assert listado.status_code == 200
    pagina = listado.json()
    validar(contrato, "ProductPage", pagina)
    # app/seed.py fija 35 unidades para el Teclado Mecánico Kappa, ID 4.
    assert [(producto["id"], producto["stock"]) for producto in pagina["items"]] == [(4, 35)]

    for respuesta in (detalle_inicial, detalle_final):
        assert respuesta.status_code == 200
        producto = respuesta.json()
        validar(contrato, "ProductOut", producto)
        assert producto["id"] == 4
        assert producto["stock"] == 35


@pytest.mark.parametrize(
    "producto_id",
    [pytest.param(39, id="inactivo"), pytest.param(999_999, id="inexistente")],
)
def test_detalle_de_producto_no_publicado_devuelve_404(api, contrato, producto_id):
    """CA-03.4 y OpenAPI GET /api/products/{product_id} → 404 ErrorOut."""
    respuesta = api.get(f"/api/products/{producto_id}")

    assert respuesta.status_code == 404
    error = respuesta.json()
    validar(contrato, "ErrorOut", error)
    assert error["detail"] == "Producto no encontrado"


def test_detalle_rechaza_identificador_no_entero(api, contrato):
    """OpenAPI GET /api/products/{product_id} · product_id debe ser entero."""
    respuesta = api.get("/api/products/no-entero")

    assert respuesta.status_code == 422
    error = respuesta.json()
    validar(contrato, "HTTPValidationError", error)
    assert ["path", "product_id"] in [detalle["loc"] for detalle in error["detail"]]
