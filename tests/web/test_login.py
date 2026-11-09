"""Lab 4.1 · Inicio de sesión (HU-02)."""
from playwright.sync_api import Page, expect

from tests.web.conftest import iniciar_sesion


def test_login_valido_muestra_el_nombre(page: Page):
    iniciar_sesion(page, "ana.garcia@example.com", "Password123")
    expect(page.locator("#user-name")).to_have_text("Ana García")
    expect(page.get_by_role("link", name="Mis órdenes")).to_be_visible()


def test_login_invalido_muestra_mensaje_generico(page: Page):  # CA-02.2
    page.goto("/login")
    page.get_by_label("Correo electrónico").fill("ana.garcia@example.com")
    page.get_by_label("Contraseña").fill("incorrecta1")
    page.get_by_role("button", name="Entrar").click()
    expect(page.get_by_role("alert")).to_have_text("Correo o contraseña incorrectos")
    expect(page).to_have_url("/login")


def test_login_con_cliente_sintetico(page: Page, cliente_sintetico):
    iniciar_sesion(page, cliente_sintetico["email"], cliente_sintetico["password"])
    expect(page.locator("#user-name")).to_have_text(cliente_sintetico["name"])


def test_cerrar_sesion(page: Page):
    iniciar_sesion(page, "ana.garcia@example.com", "Password123")
    page.get_by_role("button", name="Cerrar sesión").click()
    expect(page.get_by_role("link", name="Iniciar sesión")).to_be_visible()
