"""Fixtures para las pruebas web con Playwright.

- servidor (en tests/conftest.py): la app corriendo en un puerto libre, con su propia base de datos.
- base_url: lo usa Playwright para que page.goto("/login") vaya al servidor de pruebas.
- reiniciar_app (automático): deja los datos base antes de CADA prueba (aislamiento).
- cliente_sintetico: crea un cliente y productos con el generador del Lab 3.

Ejecutar:  pytest tests/web            (agrega --headed para ver el navegador)
"""
import pytest

from data.generador import generar_dataset
from tests.conftest import _post


@pytest.fixture(scope="session")
def base_url(servidor):
    return servidor


@pytest.fixture(autouse=True)
def reiniciar_app(servidor):
    _post(f"{servidor}/api/test/reset")


@pytest.fixture
def cliente_sintetico(servidor):
    """Un cliente nuevo (y 3 productos) creados con el generador de datos sintéticos."""
    dataset = generar_dataset(seed=19, clientes=1, productos=3)
    creados = _post(f"{servidor}/api/test/seed", dataset)
    cliente = dataset["users"][0]
    return {**cliente, "product_ids": creados["products"]}


def iniciar_sesion(page, email: str, password: str) -> None:
    """Inicia sesión por la interfaz y espera a volver al catálogo."""
    page.goto("/login")
    page.get_by_label("Correo electrónico").fill(email)
    page.get_by_label("Contraseña").fill(password)
    page.get_by_role("button", name="Entrar").click()
    page.wait_for_url("**/")
