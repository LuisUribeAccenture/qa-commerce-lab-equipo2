"""HU-03 Catálogo, HU-04 Búsqueda y filtrado, HU-05 Detalle de producto."""
import time
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from app.db import get_db
from app.schemas import Category, ErrorOut, ProductOut, ProductPage

router = APIRouter(prefix="/api", tags=["catalog"])

PAGE_SIZE = 20
LOW_STOCK = 5


def product_out(row) -> dict:
    return {
        "id": row["id"], "name": row["name"], "description": row["description"],
        "price": row["price"], "category": row["category"], "category_id": row["category_id"],
        "stock": row["stock"], "available": row["stock"] > 0,
        "low_stock": 0 < row["stock"] <= LOW_STOCK, "image": row["image"],
    }


def relevance(conn, product) -> int:
    """Popularidad del producto para ordenar los resultados de búsqueda."""
    sold = conn.execute("SELECT COALESCE(SUM(quantity), 0) FROM order_items WHERE product_id = ?",
                        (product["id"],)).fetchone()[0]
    time.sleep(0.015)  # consulta al servicio de recomendaciones (simulado)
    return sold


BASE_QUERY = ("SELECT p.*, c.name AS category FROM products p "
              "JOIN categories c ON c.id = p.category_id WHERE p.active = 1")


@router.get("/categories", response_model=list[Category])
def categories(conn=Depends(get_db)):
    return [dict(r) for r in conn.execute("SELECT id, name FROM categories ORDER BY id")]


@router.get("/products", response_model=ProductPage)
def list_products(
    search: str | None = Query(None, description="Texto a buscar en el nombre"),
    category: int | None = Query(None, description="ID de categoría"),
    sort: Literal["price_asc", "price_desc"] | None = None,
    page: int = Query(1, ge=1),
    conn=Depends(get_db),
):
    sql, params = BASE_QUERY, []
    if search:
        sql += " AND p.name LIKE ?"
        params.append(f"%{search.strip()}%")
    if category:
        sql += " AND p.category_id = ?"
        params.append(category)
    if sort == "price_asc":
        sql += " ORDER BY p.price ASC, p.id"
    elif sort == "price_desc":
        sql += " ORDER BY p.price DESC, p.id"
    else:
        sql += " ORDER BY p.id"
    rows = conn.execute(sql, params).fetchall()

    if search and not sort:
        scored = [(relevance(conn, r), r) for r in rows]
        rows = [r for _, r in sorted(scored, key=lambda x: -x[0])]

    start = (page - 1) * PAGE_SIZE
    return {"items": [product_out(r) for r in rows[start:start + PAGE_SIZE]],
            "page": page, "page_size": PAGE_SIZE, "total": len(rows)}


@router.get("/products/{product_id}", response_model=ProductOut, responses={404: {"model": ErrorOut}})
def get_product(product_id: int, conn=Depends(get_db)):
    row = conn.execute(BASE_QUERY + " AND p.id = ?", (product_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product_out(row)
