"""Desafío del Lab 4.2, resuelto.

Causa: el resumen del carrito se actualiza de forma asíncrona (entre 0.3 y 1.5 s después
del cambio). inner_text() lee el valor de ese instante, que todavía es el anterior.
Solución: una aserción web-first (expect ... to_have_text) que reintenta hasta que el
texto coincide o vence el tiempo. Sin esperas fijas y sin debilitar la aserción.
"""
from playwright.sync_api import Page, expect

from tests.web.conftest import iniciar_sesion


def test_cambiar_cantidad_actualiza_el_total(page: Page):
    iniciar_sesion(page, "ana.garcia@example.com", "Password123")
    page.goto("/productos/4")  # Teclado Mecánico Kappa, $1,299.00
    page.get_by_role("button", name="Agregar al carrito").click()
    expect(page.locator(".flash.ok")).to_be_visible()

    page.goto("/carrito")
    cantidad = page.get_by_label("Cantidad de Teclado Mecánico Kappa")
    cantidad.fill("2")
    cantidad.press("Tab")

    expect(page.locator("#sum-total")).to_have_text("$2,598.00")
