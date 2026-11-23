from playwright.sync_api import Page, expect


class CheckoutPage:
    def __init__(self, page: Page):
        self._page = page
        self._total = page.locator("#co-total")
        self._calle = page.get_by_label("Calle y número", exact=True)
        self._colonia = page.get_by_label("Colonia", exact=True)
        self._ciudad = page.get_by_label("Ciudad", exact=True)
        self._estado = page.get_by_label("Estado", exact=True)
        self._codigo_postal = page.get_by_label("Código postal", exact=True)
        self._telefono = page.get_by_label("Teléfono de contacto", exact=True)
        self._confirmar = page.get_by_role("button", name="Confirmar y pagar", exact=True)

    def abrir(self) -> None:
        self._page.goto("/checkout")

    def confirmar_direccion(
        self, *, calle: str, colonia: str, ciudad: str, estado: str, codigo_postal: str, telefono: str
    ) -> None:
        expect(self._total).not_to_be_empty()
        self._calle.fill(calle)
        self._colonia.fill(colonia)
        self._ciudad.fill(ciudad)
        self._estado.fill(estado)
        self._codigo_postal.fill(codigo_postal)
        self._telefono.fill(telefono)
        self._confirmar.click()
        self._page.wait_for_url("**/pago/*")
