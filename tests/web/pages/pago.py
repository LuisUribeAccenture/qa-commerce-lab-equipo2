from playwright.sync_api import Page, expect


class PagoPage:
    def __init__(self, page: Page):
        self._total = page.locator("#pay-total")
        self._titular = page.get_by_label("Nombre del titular", exact=True)
        self._numero = page.get_by_label("Número de tarjeta", exact=True)
        self._vencimiento = page.get_by_label("Vencimiento (MM/AA)", exact=True)
        self._cvv = page.get_by_label("CVV", exact=True)
        self._pagar = page.get_by_role("button", name="Pagar", exact=True)
        self.confirmacion = page.locator("#confirmation")
        self.ultimos_cuatro = page.locator("#confirm-last4")
        self.error = page.get_by_role("alert")

    def pagar(self, *, titular: str, numero: str, vencimiento: str, cvv: str) -> None:
        expect(self._total).not_to_be_empty()
        self._titular.fill(titular)
        self._numero.fill(numero)
        self._vencimiento.fill(vencimiento)
        self._cvv.fill(cvv)
        self._pagar.click()
