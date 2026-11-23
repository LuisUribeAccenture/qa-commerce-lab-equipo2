from playwright.sync_api import Page, expect


class ProductoPage:
    def __init__(self, page: Page):
        self._page = page
        self._cantidad = page.get_by_label("Cantidad", exact=True)
        self._agregar = page.get_by_role("button", name="Agregar al carrito", exact=True)
        self._aviso = page.get_by_role("status")

    def abrir(self, producto_id: int) -> None:
        self._page.goto(f"/productos/{producto_id}")

    def agregar_al_carrito(self, cantidad: int) -> None:
        self._cantidad.fill(str(cantidad))
        self._agregar.click()
        expect(self._aviso).to_have_text("Producto agregado al carrito")

