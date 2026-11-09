"""Cálculo de totales, envío y cupones (HU-08, HU-09, RN-07, RN-08)."""
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

SHIPPING_COST = Decimal("99.00")
FREE_SHIPPING_THRESHOLD = Decimal("999.00")


def money(value) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def coupon_error(coupon, subtotal: Decimal, paid_orders: int, today: date | None = None) -> str | None:
    """Devuelve None si el cupón aplica, o el motivo por el que no aplica."""
    today = today or date.today()
    if coupon is None:
        return "Cupón no válido"
    if coupon["valid_until"] and today > date.fromisoformat(coupon["valid_until"]):
        return "Cupón no válido"
    if subtotal < money(coupon["min_subtotal"]):
        return "Cupón no válido"
    if coupon["first_purchase_only"] and paid_orders > 0:
        return "Cupón no válido"
    return None


def compute_totals(items, coupon=None, paid_orders: int = 0) -> dict:
    """items: lista de dicts con price y quantity. coupon: fila de la tabla coupons o None."""
    subtotal = money(sum(money(i["price"]) * i["quantity"] for i in items))
    discount = Decimal("0.00")
    shipping = SHIPPING_COST if items else Decimal("0.00")

    # Envío gratis en compras mayores a $999.00
    if subtotal >= FREE_SHIPPING_THRESHOLD:
        shipping = Decimal("0.00")

    applied = None
    if coupon is not None and items and coupon_error(coupon, subtotal, paid_orders) is None:
        applied = coupon["code"]
        if coupon["kind"] == "percent":
            discount = money(subtotal * Decimal(str(coupon["value"])) / 100)
        elif coupon["kind"] == "fixed":
            discount = min(money(coupon["value"]), subtotal)
        elif coupon["kind"] == "shipping":
            shipping = Decimal("0.00")

    total = money(subtotal - discount + shipping)
    return {
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping,
        "total": total,
        "coupon_code": applied,
    }
