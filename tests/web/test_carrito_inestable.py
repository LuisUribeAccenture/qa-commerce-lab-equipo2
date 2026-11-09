"""Desafío del Lab 4.2: esta prueba falla de forma intermitente.

Encuentren por qué y corríjanla SIN agregar esperas fijas (time.sleep o wait_for_timeout)
y SIN debilitar la aserción. Ejecútenla varias veces para comprobarlo:
    pytest tests/web/test_carrito_inestable.py   (ejecútenla 4 o 5 veces)
"""
from playwright.sync_api import Page

from tests.web.conftest import iniciar_sesion


def test_cambiar_cantidad_actualiza_el_total(page: Page):
    iniciar_sesion(page, "ana.garcia@example.com", "Password123")
    page.goto("/productos/4")  # Teclado Mecánico Kappa, $1,299.00
    page.get_by_role("button", name="Agregar al carrito").click()
    page.locator(".flash.ok").wait_for()

    page.goto("/carrito")
    page.get_by_label("Cantidad de Teclado Mecánico Kappa").fill("2")
    page.get_by_label("Cantidad de Teclado Mecánico Kappa").press("Tab")
    page.locator(".line-total", has_text="$2,598.00").wait_for()

    total = page.locator("#sum-total").inner_text()
    assert total == "$2,598.00"
