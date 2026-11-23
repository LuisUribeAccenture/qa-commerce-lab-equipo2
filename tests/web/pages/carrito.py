from playwright.sync_api import Page, expect


class CarritoPage:
    def __init__(self, page: Page):
        self._page = page
        self._productos = page.get_by_role("region", name="Productos en el carrito", exact=True)
        self._cupon = page.get_by_label("Cupón", exact=True)
        self._aplicar = page.get_by_role("button", name="Aplicar", exact=True)
        self._continuar = page.get_by_role("link", name="Continuar al checkout", exact=True)
        self.descuento = page.locator("#sum-discount")
        self.total = page.locator("#sum-total")

    def abrir(self) -> None:
        self._page.goto("/carrito")
        expect(self._productos).not_to_be_empty()

    def aplicar_cupon(self, codigo: str) -> None:
        self._cupon.fill(codigo)
        self._aplicar.click()

    def continuar_al_checkout(self) -> None:
        self._continuar.click()
