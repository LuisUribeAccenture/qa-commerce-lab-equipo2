"""Endpoints de apoyo para pruebas automatizadas: reinicio y carga de datos.

Solo existen en el entorno de laboratorio (QACL_TEST_ENDPOINTS=1, valor por defecto).
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.db import get_db, init_db
from app.security import hash_password, now

router = APIRouter(prefix="/api/test", tags=["testing"])

ORDER_STATUSES = ("Pendiente de pago", "Pagada", "Enviada", "Entregada", "Cancelada")


class SeedUser(BaseModel):
    name: str
    email: str
    password: str
    birth_date: str = "1990-01-01"


class SeedProduct(BaseModel):
    name: str
    description: str = "Producto de prueba"
    price: float
    category: str = "Accesorios"
    stock: int = 10
    active: bool = True


class SeedCoupon(BaseModel):
    code: str
    kind: str  # percent | fixed | shipping
    value: float
    min_subtotal: float = 0
    first_purchase_only: bool = False
    valid_until: str | None = None


class SeedIn(BaseModel):
    users: list[SeedUser] = []
    products: list[SeedProduct] = []
    coupons: list[SeedCoupon] = []


class OrderStatusIn(BaseModel):
    status: str
    paid_at: str | None = None


@router.post("/reset")
def reset():
    """Borra todo y vuelve a cargar los datos base."""
    init_db(reset=True)
    return {"status": "ok"}


@router.post("/seed")
def seed(data: SeedIn, conn=Depends(get_db)):
    """Agrega usuarios, productos y cupones sobre los datos actuales."""
    created = {"users": [], "products": [], "coupons": []}
    for u in data.users:
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash, birth_date, created_at) VALUES (?, ?, ?, ?, ?)",
            (u.name, u.email, hash_password(u.password), u.birth_date, now().isoformat()))
        created["users"].append(cur.lastrowid)
    for p in data.products:
        cat = conn.execute("SELECT id FROM categories WHERE name = ?", (p.category,)).fetchone()
        if cat is None:
            raise HTTPException(status_code=400, detail=f"Categoría desconocida: {p.category}")
        cur = conn.execute(
            "INSERT INTO products (name, description, price, category_id, stock, active, image) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (p.name, p.description, p.price, cat["id"], p.stock, int(p.active), f"/static/img/{cat['id']}.svg"))
        created["products"].append(cur.lastrowid)
    for c in data.coupons:
        conn.execute("INSERT OR REPLACE INTO coupons VALUES (?, ?, ?, ?, ?, ?)",
                     (c.code.upper(), c.kind, c.value, c.min_subtotal, int(c.first_purchase_only), c.valid_until))
        created["coupons"].append(c.code.upper())
    return created


@router.post("/orders/{order_id}/status")
def force_order_status(order_id: int, data: OrderStatusIn, conn=Depends(get_db)):
    """Cambia el estado de una orden (por ejemplo, para simular que ya fue enviada)."""
    if data.status not in ORDER_STATUSES:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Usa uno de: {', '.join(ORDER_STATUSES)}")
    if not conn.execute("SELECT 1 FROM orders WHERE id = ?", (order_id,)).fetchone():
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    if data.paid_at:
        conn.execute("UPDATE orders SET status = ?, paid_at = ? WHERE id = ?", (data.status, data.paid_at, order_id))
    else:
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (data.status, order_id))
    return {"status": "ok"}
