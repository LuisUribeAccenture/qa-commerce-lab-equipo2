"""Ejemplo de prueba de API: estado, contrato y regla de negocio. Úsenla como modelo."""
from tests.api.contrato import validar


def test_listar_productos(api, contrato):
    res = api.get("/api/products")

    assert res.status_code == 200                       # 1. estado HTTP
    validar(contrato, "ProductPage", res.json())        # 2. cumple el contrato
    datos = res.json()
    assert datos["page_size"] == 20                     # 3. regla de negocio (CA-03.2)
    assert len(datos["items"]) == 20
