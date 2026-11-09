"""Lab 4.2 · Carrito y checkout (HU-06 a HU-10)."""
import pytest
from playwright.sync_api import Page, expect

from tests.web.conftest import iniciar_sesion


@pytest.fixture
def ana(page: Page) -> Page:
    iniciar_sesion(page, "ana.garcia@example.com", "Password123")
    return page


def agregar(page: Page, product_id: int, cantidad: int) -> None:
    page.goto(f"/productos/{product_id}")
    page.get_by_label("Cantidad").fill(str(cantidad))
    page.get_by_role("button", name="Agregar al carrito").click()
    expect(page.locator(".flash.ok")).to_have_text("Producto agregado al carrito")


def test_agregar_actualiza_el_contador(ana: Page):  # CA-06.5
    agregar(ana, 4, 2)
    expect(ana.locator("#cart-count")).to_have_text("2")


def test_resumen_con_envio(ana: Page):  # CA-09.2 a CA-09.4
    agregar(ana, 4, 2)  # 2 x $1,299.00
    ana.goto("/carrito")
    expect(ana.locator("#sum-subtotal")).to_have_text("$2,598.00")
    expect(ana.locator("#sum-shipping")).to_have_text("Gratis")  # subtotal > $999
    expect(ana.locator("#sum-total")).to_have_text("$2,598.00")


def test_resumen_debajo_del_umbral(ana: Page):  # RN-08
    agregar(ana, 25, 1)  # Foco Inteligente RGB, $249.00
    ana.goto("/carrito")
    expect(ana.locator("#sum-shipping")).to_have_text("$99.00")
    expect(ana.locator("#sum-total")).to_have_text("$348.00")


def test_cantidad_mayor_a_10_se_rechaza_en_la_web(ana: Page):  # RN-05
    ana.goto("/productos/4")
    ana.get_by_label("Cantidad").fill("11")
    ana.get_by_role("button", name="Agregar al carrito").click()
    expect(ana.get_by_role("alert")).to_have_text("La cantidad debe estar entre 1 y 10")


def test_cupon_vencido(ana: Page):  # sección 4.2
    agregar(ana, 4, 1)
    ana.goto("/carrito")
    ana.get_by_label("Cupón").fill("NAVIDAD25")
    ana.get_by_role("button", name="Aplicar").click()
    expect(ana.locator("#coupon-error")).to_have_text("Cupón no válido")


def test_cupon_bienvenida(ana: Page):
    agregar(ana, 4, 2)  # $2,598.00 -> 10% = $259.80
    ana.goto("/carrito")
    ana.get_by_label("Cupón").fill("BIENVENIDA10")
    ana.get_by_role("button", name="Aplicar").click()
    expect(ana.locator("#sum-discount")).to_have_text("-$259.80")
    expect(ana.locator("#sum-total")).to_have_text("$2,338.20")


def test_carrito_vacio(ana: Page):  # CA-07.5
    ana.goto("/carrito")
    expect(ana.get_by_text("Tu carrito está vacío")).to_be_visible()
    # Sin href, el <a> deja de ser un enlace accesible: se localiza por id
    expect(ana.locator("#go-checkout")).to_have_attribute("aria-disabled", "true")


@pytest.mark.xfail(strict=True, reason="BUG-02: con subtotal de $999.00 el carrito y el checkout muestran totales distintos (RN-08)")
def test_carrito_y_checkout_coinciden_en_el_umbral(ana: Page):
    agregar(ana, 5, 2)  # 2 x $499.50 = $999.00
    ana.goto("/carrito")
    expect(ana.locator("#sum-subtotal")).to_have_text("$999.00")
    total_carrito = ana.locator("#sum-total").inner_text()

    ana.get_by_role("link", name="Continuar al checkout").click()
    expect(ana.locator("#co-total")).not_to_be_empty()
    expect(ana.locator("#co-total")).to_have_text(total_carrito)
