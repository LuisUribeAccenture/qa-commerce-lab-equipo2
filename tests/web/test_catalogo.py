"""Lab 4.1 · Catálogo, búsqueda y filtros (HU-03, HU-04)."""
import re

from playwright.sync_api import Page, expect


def precio(texto: str) -> float:
    return float(re.sub(r"[^\d.]", "", texto))


def test_buscar_por_nombre(page: Page):
    page.goto("/")
    page.get_by_label("Buscar").fill("Laptop")
    page.get_by_role("button", name="Buscar").click()
    tarjetas = page.get_by_test_id("product-card")
    expect(tarjetas).to_have_count(4)  # 2 laptops, la mochila y la base refrigerante
    nombres = tarjetas.get_by_role("heading").all_inner_texts()
    assert all("Laptop" in n for n in nombres)
    assert "Laptop Nébula 13 (2023)" not in nombres  # inactiva: no debe aparecer (CA-03.4)


def test_busqueda_sin_resultados(page: Page):  # CA-04.5
    page.goto("/?search=zzzz")
    expect(page.locator("#results-info")).to_have_text("No encontramos productos para tu búsqueda")
    expect(page.get_by_test_id("product-card")).to_have_count(0)


def test_filtrar_por_categoria(page: Page):
    page.goto("/")
    page.get_by_label("Categoría").select_option(label="Audio")
    page.get_by_role("button", name="Buscar").click()
    expect(page.get_by_test_id("product-card").first).to_be_visible()
    categorias = page.get_by_test_id("product-card").locator(".muted").all_inner_texts()
    assert categorias and set(categorias) == {"Audio"}


def test_ordenar_por_precio_ascendente(page: Page):
    page.goto("/?sort=price_asc")
    expect(page.get_by_test_id("product-card").first).to_be_visible()
    precios = [precio(t) for t in page.locator(".price").all_inner_texts()]
    assert precios == sorted(precios)


def test_producto_agotado_no_se_puede_agregar(page: Page):  # CA-03.3
    page.goto("/?search=Disco SSD")
    tarjeta = page.get_by_test_id("product-card").filter(has_text="Disco SSD Externo 1 TB")
    expect(tarjeta.get_by_text("Agotado")).to_be_visible()
    expect(tarjeta.get_by_role("button", name=re.compile("Agregar"))).to_be_disabled()
