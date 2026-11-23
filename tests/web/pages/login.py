from playwright.sync_api import Page

from tests.web.conftest import iniciar_sesion


class LoginPage:
    def __init__(self, page: Page):
        self._page = page

    def iniciar_sesion(self, correo: str, contrasena: str) -> None:
        iniciar_sesion(self._page, correo, contrasena)
