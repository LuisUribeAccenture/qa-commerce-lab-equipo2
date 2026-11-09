"""HU-10 Checkout, HU-11 Pago simulado, HU-12 Historial y cancelación."""
import json
import logging
import re
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.db import get_db
from app.pricing import compute_totals
from app.routes.cart import cart_coupon, cart_items, paid_orders
from app.schemas import ErrorOut, OrderIn, OrderOut, OrderSummary, PaymentIn
from app.security import current_user, now

router = APIRouter(prefix="/api/orders", tags=["orders"])
log = logging.getLogger("qacl.orders")

CANCEL_WINDOW = timedelta(hours=24)

CARD_RESULTS = {
    "4111111111111111": (True, None),
    "4000000000000002": (False, "Fondos insuficientes"),
    "4000000000000069": (False, "Tarjeta vencida"),
}
REJECTED = "Pago rechazado. Verifica tus datos o usa otra tarjeta."


def order_out(conn, order) -> dict:
    items = conn.execute("SELECT product_id, name, unit_price, quantity FROM order_items WHERE order_id = ?",
                         (order["id"],)).fetchall()
    data = dict(order)
    data.pop("user_id")
    data["address"] = json.loads(order["address"])
    data["items"] = [dict(i) for i in items]
    return data


def own_order(conn, order_id: int, user_id: int):
    order = conn.execute("SELECT * FROM orders WHERE id = ? AND user_id = ?", (order_id, user_id)).fetchone()
    if order is None:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return order


@router.post("", response_model=OrderOut, status_code=201,
             responses={400: {"model": ErrorOut}, 409: {"model": ErrorOut}})
def create_order(data: OrderIn, auth=Depends(current_user), conn=Depends(get_db)):
    user = auth["user"]
    items = cart_items(conn, user["id"])
    if not items:
        raise HTTPException(status_code=400, detail="Tu carrito está vacío")

    addr = data.address
    errors = {f: "Campo obligatorio" for f, v in addr.model_dump().items() if not v.strip()}
    if addr.postal_code.strip() and not re.fullmatch(r"\d{5}", addr.postal_code.strip()):
        errors["postal_code"] = "El código postal debe tener 5 dígitos"
        log.warning("Dirección rechazada para %s: %s", user["email"], addr.model_dump())
        return JSONResponse(status_code=400, content={
            "detail": f"No pudimos validar la dirección de {user['name']} (tel. {addr.phone}): "
                      "el código postal debe tener 5 dígitos",
            "errors": errors})
    if addr.phone.strip() and not re.fullmatch(r"\d{10}", addr.phone.strip()):
        errors["phone"] = "El teléfono debe tener 10 dígitos"
    if errors:
        return JSONResponse(status_code=400, content={"detail": "Revisa la dirección de envío", "errors": errors})

    for i in items:
        if i["quantity"] > i["stock"]:
            raise HTTPException(status_code=409, detail=f"No hay existencias suficientes de {i['name']}")

    totals = compute_totals(items, cart_coupon(conn, user["id"]), paid_orders(conn, user["id"]))
    address_json = json.dumps(addr.model_dump(), ensure_ascii=False)
    cur = conn.execute(
        "INSERT INTO orders (user_id, status, subtotal, discount, shipping, total, coupon_code, address, created_at) "
        "VALUES (?, 'Pendiente de pago', ?, ?, ?, ?, ?, ?, ?)",
        (user["id"], float(totals["subtotal"]), float(totals["discount"]), float(totals["shipping"]),
         float(totals["total"]), totals["coupon_code"], address_json, now().isoformat()))
    for i in items:
        conn.execute("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)",
                     (cur.lastrowid, i["product_id"], i["name"], i["price"], i["quantity"]))
    if data.save_address:
        conn.execute("UPDATE users SET saved_address = ? WHERE id = ?", (address_json, user["id"]))
    return order_out(conn, conn.execute("SELECT * FROM orders WHERE id = ?", (cur.lastrowid,)).fetchone())


def validate_card(data: PaymentIn) -> dict:
    errors = {}
    number = re.sub(r"\s", "", data.card_number)
    if not data.card_holder.strip():
        errors["card_holder"] = "El nombre del titular es obligatorio"
    if not re.fullmatch(r"\d{16}", number):
        errors["card_number"] = "El número de tarjeta debe tener 16 dígitos"
    m = re.fullmatch(r"(\d{2})/(\d{2})", data.expiry.strip())
    if not m or not 1 <= int(m.group(1)) <= 12:
        errors["expiry"] = "La fecha de vencimiento debe tener el formato MM/AA"
    else:
        month, year = int(m.group(1)), 2000 + int(m.group(2))
        today = now()
        if (year, month) < (today.year, today.month):
            errors["expiry"] = "La tarjeta está vencida"
    if not re.fullmatch(r"\d{3}", data.cvv.strip()):
        errors["cvv"] = "El CVV debe tener 3 dígitos"
    return errors


@router.post("/{order_id}/pay", response_model=OrderOut,
             responses={400: {"model": ErrorOut}, 402: {"model": ErrorOut}, 409: {"model": ErrorOut}})
def pay_order(order_id: int, data: PaymentIn, auth=Depends(current_user), conn=Depends(get_db)):
    user_id = auth["user"]["id"]
    order = own_order(conn, order_id, user_id)
    if order["status"] != "Pendiente de pago":
        raise HTTPException(status_code=409, detail="La orden ya fue procesada")
    errors = validate_card(data)
    if errors:
        return JSONResponse(status_code=400, content={"detail": "Revisa los datos de la tarjeta", "errors": errors})

    number = re.sub(r"\s", "", data.card_number)
    approved, reason = CARD_RESULTS.get(number, (False, "Tarjeta no reconocida"))
    if not approved:
        return JSONResponse(status_code=402, content={"detail": REJECTED, "errors": {"card_number": reason}})

    items = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
    for i in items:
        stock = conn.execute("SELECT stock FROM products WHERE id = ?", (i["product_id"],)).fetchone()["stock"]
        if i["quantity"] > stock:
            raise HTTPException(status_code=409, detail=f"No hay existencias suficientes de {i['name']}")
    for i in items:
        conn.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (i["quantity"], i["product_id"]))
    conn.execute("UPDATE orders SET status = 'Pagada', paid_at = ?, card_last4 = ? WHERE id = ?",
                 (now().isoformat(), number[-4:], order_id))
    conn.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))
    conn.execute("UPDATE carts SET coupon_code = NULL WHERE user_id = ?", (user_id,))
    return order_out(conn, conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone())


@router.get("", response_model=list[OrderSummary])
def list_orders(auth=Depends(current_user), conn=Depends(get_db)):
    rows = conn.execute("SELECT id, status, total, created_at FROM orders WHERE user_id = ? "
                        "ORDER BY created_at DESC, id DESC", (auth["user"]["id"],))
    return [dict(r) for r in rows]


@router.get("/{order_id}", response_model=OrderOut, responses={404: {"model": ErrorOut}})
def get_order(order_id: int, auth=Depends(current_user), conn=Depends(get_db)):
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if order is None:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return order_out(conn, order)


@router.post("/{order_id}/cancel", response_model=OrderOut,
             responses={404: {"model": ErrorOut}, 409: {"model": ErrorOut}})
def cancel_order(order_id: int, auth=Depends(current_user), conn=Depends(get_db)):
    order = own_order(conn, order_id, auth["user"]["id"])
    if order["status"] != "Pagada" or now() - datetime.fromisoformat(order["paid_at"]) > CANCEL_WINDOW:
        raise HTTPException(status_code=409, detail="La orden ya no se puede cancelar")
    for i in conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall():
        conn.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (i["quantity"], i["product_id"]))
    conn.execute("UPDATE orders SET status = 'Cancelada' WHERE id = ?", (order_id,))
    return order_out(conn, conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone())
