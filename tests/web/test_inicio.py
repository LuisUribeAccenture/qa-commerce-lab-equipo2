"""Ejemplo de prueba web. Úsenla como modelo para las suyas."""
from playwright.sync_api import Page, expect


def test_el_catalogo_muestra_la_primera_pagina(page: Page):
    page.goto("/")
    expect(page.get_by_role("heading", name="Catálogo")).to_be_visible()
    expect(page.get_by_test_id("product-card")).to_have_count(20)
    expect(page.locator("#results-info")).to_have_text("38 productos")
