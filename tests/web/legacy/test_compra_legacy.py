# Pruebas heredadas de otro equipo. Funcionan… casi siempre.
# Lab 5.1: refactorícenlas con Page Objects. No cambien QUÉ verifican, solo CÓMO.
import time


def test_compra_completa(page, base_url):
    page.goto(base_url + "/login")
    page.fill("#login-email", "ana.garcia@example.com")
    page.fill("#login-password", "Password123")
    page.click("form#login-form > button")
    time.sleep(1)
    page.goto(base_url + "/productos/4")
    time.sleep(1)
    page.fill("#qty", "2")
    page.click("#add-form > button")
    time.sleep(1)
    page.goto(base_url + "/carrito")
    time.sleep(2)
    assert page.inner_text("#sum-total") == "$2,598.00"
    page.click("#go-checkout")
    time.sleep(1)
    page.fill("#addr-street", "Calle 1")
    page.fill("#addr-neighborhood", "Centro")
    page.fill("#addr-city", "Monterrey")
    page.fill("#addr-state", "Nuevo León")
    page.fill("#addr-postal", "64000")
    page.fill("#addr-phone", "8112345678")
    page.click("#address-form > button")
    time.sleep(2)
    page.fill("#card-holder", "Ana García")
    page.fill("#card-number", "4111 1111 1111 1111")
    page.fill("#card-expiry", "12/30")
    page.fill("#card-cvv", "123")
    page.click("#payment-form > button")
    time.sleep(2)
    assert "Gracias" in page.inner_text("#confirmation")
    assert page.inner_text("#confirm-last4") == "1111"


def test_compra_con_tarjeta_rechazada(page, base_url):
    page.goto(base_url + "/login")
    page.fill("#login-email", "ana.garcia@example.com")
    page.fill("#login-password", "Password123")
    page.click("form#login-form > button")
    time.sleep(1)
    page.goto(base_url + "/productos/4")
    time.sleep(1)
    page.fill("#qty", "1")
    page.click("#add-form > button")
    time.sleep(1)
    page.goto(base_url + "/checkout")
    time.sleep(2)
    page.fill("#addr-street", "Calle 1")
    page.fill("#addr-neighborhood", "Centro")
    page.fill("#addr-city", "Monterrey")
    page.fill("#addr-state", "Nuevo León")
    page.fill("#addr-postal", "64000")
    page.fill("#addr-phone", "8112345678")
    page.click("#address-form > button")
    time.sleep(2)
    page.fill("#card-holder", "Ana García")
    page.fill("#card-number", "4000 0000 0000 0002")
    page.fill("#card-expiry", "12/30")
    page.fill("#card-cvv", "123")
    page.click("#payment-form > button")
    time.sleep(2)
    assert page.inner_text("#payment-error") == "Pago rechazado. Verifica tus datos o usa otra tarjeta."


def test_cupon_bienvenida_en_carrito(page, base_url):
    page.goto(base_url + "/login")
    page.fill("#login-email", "ana.garcia@example.com")
    page.fill("#login-password", "Password123")
    page.click("form#login-form > button")
    time.sleep(1)
    page.goto(base_url + "/productos/4")
    time.sleep(1)
    page.fill("#qty", "2")
    page.click("#add-form > button")
    time.sleep(1)
    page.goto(base_url + "/carrito")
    time.sleep(1)
    page.fill("#coupon-code", "BIENVENIDA10")
    page.click("#coupon-form button")
    time.sleep(3)
    assert page.inner_text("#sum-discount") == "-$259.80"
    assert page.inner_text("#sum-total") == "$2,338.20"
