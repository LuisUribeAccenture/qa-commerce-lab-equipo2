from playwright.sync_api import Page, expect

from tests.web.pages.carrito import CarritoPage
from tests.web.pages.checkout import CheckoutPage
from tests.web.pages.login import LoginPage
from tests.web.pages.pago import PagoPage
from tests.web.pages.producto import ProductoPage

DIRECCION = {
    "calle": "Calle 1",
    "colonia": "Centro",
    "ciudad": "Monterrey",
    "estado": "Nuevo León",
    "codigo_postal": "64000",
    "telefono": "8112345678",
}


def preparar_compra(page: Page, cantidad: int) -> None:
    LoginPage(page).iniciar_sesion("ana.garcia@example.com", "Password123")
    producto = ProductoPage(page)
    producto.abrir(4)
    producto.agregar_al_carrito(cantidad)


def test_compra_completa(page: Page) -> None:
    preparar_compra(page, cantidad=2)
    carrito = CarritoPage(page)
    carrito.abrir()
    expect(carrito.total).to_have_text("$2,598.00", use_inner_text=True)

    carrito.continuar_al_checkout()
    CheckoutPage(page).confirmar_direccion(**DIRECCION)
    pago = PagoPage(page)
    pago.pagar(titular="Ana García", numero="4111 1111 1111 1111", vencimiento="12/30", cvv="123")

    expect(pago.confirmacion).to_contain_text("Gracias", use_inner_text=True)
    expect(pago.ultimos_cuatro).to_have_text("1111", use_inner_text=True)


def test_compra_con_tarjeta_rechazada(page: Page) -> None:
    preparar_compra(page, cantidad=1)
    checkout = CheckoutPage(page)
    checkout.abrir()
    checkout.confirmar_direccion(**DIRECCION)
    pago = PagoPage(page)
    pago.pagar(titular="Ana García", numero="4000 0000 0000 0002", vencimiento="12/30", cvv="123")

    expect(pago.error).to_have_text("Pago rechazado. Verifica tus datos o usa otra tarjeta.", use_inner_text=True)


def test_cupon_bienvenida_en_carrito(page: Page) -> None:
    preparar_compra(page, cantidad=2)
    carrito = CarritoPage(page)
    carrito.abrir()
    carrito.aplicar_cupon("BIENVENIDA10")

    expect(carrito.descuento).to_have_text("-$259.80", use_inner_text=True)
    expect(carrito.total).to_have_text("$2,338.20", use_inner_text=True)
