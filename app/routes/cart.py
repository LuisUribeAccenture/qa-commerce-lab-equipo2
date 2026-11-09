"""HU-06 Agregar al carrito, HU-07 Modificar carrito, HU-08 Cupones, HU-09 Totales."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.db import get_db
from app.pricing import compute_totals, coupon_error, money
from app.schemas import CartItemIn, CartOut, CartQuantityIn, CouponIn, ErrorOut
from app.security import current_user

router = APIRouter(prefix="/api/cart", tags=["cart"])

MAX_QTY = 10
PAID_STATUSES = ("Pagada", "Enviada", "Entregada")


def paid_orders(conn, user_id: int) -> int:
    return conn.execute(
        f"SELECT COUNT(*) FROM orders WHERE user_id = ? AND status IN ({','.join('?' * len(PAID_STATUSES))})",
        (user_id, *PAID_STATUSES)).fetchone()[0]


def cart_items(conn, user_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT ci.product_id, ci.quantity, p.name, p.price, p.stock, p.image FROM cart_items ci "
        "JOIN products p ON p.id = ci.product_id WHERE ci.user_id = ? ORDER BY p.name", (user_id,))
    return [dict(r) for r in rows]


def cart_coupon(conn, user_id: int):
    row = conn.execute("SELECT coupon_code FROM carts WHERE user_id = ?", (user_id,)).fetchone()
    if row is None or row["coupon_code"] is None:
        return None
    return conn.execute("SELECT * FROM coupons WHERE code = ?", (row["coupon_code"],)).fetchone()


def build_cart(conn, user_id: int) -> dict:
    items = cart_items(conn, user_id)
    totals = compute_totals(items, cart_coupon(conn, user_id), paid_orders(conn, user_id))
    return {
        "items": [{
            "product_id": i["product_id"], "name": i["name"], "price": i["price"],
            "quantity": i["quantity"], "line_total": float(money(i["price"]) * i["quantity"]),
            "stock": i["stock"], "image": i["image"],
        } for i in items],
        "item_count": sum(i["quantity"] for i in items),
        "subtotal": float(totals["subtotal"]),
        "discount": f"{totals['discount']:.2f}",
        "shipping": float(totals["shipping"]),
        "total": float(totals["total"]),
        "coupon_code": totals["coupon_code"],
    }


def cart_response(conn, user_id: int) -> JSONResponse:
    return JSONResponse(content=build_cart(conn, user_id))


def validate_quantity(quantity: int, stock: int) -> None:
    if quantity < 1 or quantity > MAX_QTY + 1:
        raise HTTPException(status_code=400, detail=f"La cantidad debe estar entre 1 y {MAX_QTY}")
    if quantity > stock:
        raise HTTPException(status_code=409, detail=f"Solo hay {stock} unidades disponibles")


def active_product(conn, product_id: int):
    product = conn.execute("SELECT * FROM products WHERE id = ? AND active = 1", (product_id,)).fetchone()
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.get("", response_model=CartOut, responses={401: {"model": ErrorOut}})
def get_cart(auth=Depends(current_user), conn=Depends(get_db)):
    return cart_response(conn, auth["user"]["id"])


@router.post("/items", response_model=CartOut,
             responses={400: {"model": ErrorOut}, 404: {"model": ErrorOut}, 409: {"model": ErrorOut}})
def add_item(data: CartItemIn, auth=Depends(current_user), conn=Depends(get_db)):
    user_id = auth["user"]["id"]
    product = active_product(conn, data.product_id)
    if product["stock"] == 0:
        raise HTTPException(status_code=409, detail="Producto agotado")
    existing = conn.execute("SELECT quantity FROM cart_items WHERE user_id = ? AND product_id = ?",
                            (user_id, data.product_id)).fetchone()
    new_qty = (existing["quantity"] if existing else 0) + data.quantity
    if data.quantity < 1:
        raise HTTPException(status_code=400, detail=f"La cantidad debe estar entre 1 y {MAX_QTY}")
    validate_quantity(new_qty, product["stock"])
    conn.execute(
        "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id, product_id) DO UPDATE SET quantity = excluded.quantity",
        (user_id, data.product_id, new_qty))
    return cart_response(conn, user_id)


@router.patch("/items/{product_id}", response_model=CartOut,
              responses={400: {"model": ErrorOut}, 404: {"model": ErrorOut}, 409: {"model": ErrorOut}})
def update_item(product_id: int, data: CartQuantityIn, auth=Depends(current_user), conn=Depends(get_db)):
    user_id = auth["user"]["id"]
    if not conn.execute("SELECT 1 FROM cart_items WHERE user_id = ? AND product_id = ?",
                        (user_id, product_id)).fetchone():
        raise HTTPException(status_code=404, detail="El producto no está en el carrito")
    if data.quantity == 0:
        conn.execute("DELETE FROM cart_items WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    else:
        product = active_product(conn, product_id)
        validate_quantity(data.quantity, product["stock"])
        conn.execute("UPDATE cart_items SET quantity = ? WHERE user_id = ? AND product_id = ?",
                     (data.quantity, user_id, product_id))
    return cart_response(conn, user_id)


@router.delete("/items/{product_id}", response_model=CartOut)
def remove_item(product_id: int, auth=Depends(current_user), conn=Depends(get_db)):
    user_id = auth["user"]["id"]
    conn.execute("DELETE FROM cart_items WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    return cart_response(conn, user_id)


@router.post("/coupon", response_model=CartOut, responses={400: {"model": ErrorOut}})
def apply_coupon(data: CouponIn, auth=Depends(current_user), conn=Depends(get_db)):
    user_id = auth["user"]["id"]
    code = data.code.strip().upper()
    coupon = conn.execute("SELECT * FROM coupons WHERE code = ?", (code,)).fetchone()
    items = cart_items(conn, user_id)
    subtotal = compute_totals(items)["subtotal"]
    if not items or coupon_error(coupon, subtotal, paid_orders(conn, user_id)):
        raise HTTPException(status_code=400, detail="Cupón no válido")
    conn.execute("INSERT INTO carts (user_id, coupon_code) VALUES (?, ?) "
                 "ON CONFLICT(user_id) DO UPDATE SET coupon_code = excluded.coupon_code", (user_id, code))
    return cart_response(conn, user_id)


@router.delete("/coupon", response_model=CartOut)
def remove_coupon(auth=Depends(current_user), conn=Depends(get_db)):
    user_id = auth["user"]["id"]
    conn.execute("UPDATE carts SET coupon_code = NULL WHERE user_id = ?", (user_id,))
    return cart_response(conn, user_id)
