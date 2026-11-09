"""QA Commerce Lab: API REST + aplicación web."""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db import init_db
from app.routes import auth, cart, orders, products, testing

BASE = Path(__file__).resolve().parent
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="QA Commerce Lab API",
    version="1.0.0",
    description="API de la tienda ficticia QA Commerce Lab. Sistema creado para capacitación en Testing & QA.",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
if os.environ.get("QACL_TEST_ENDPOINTS", "1") == "1":
    app.include_router(testing.router)

app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok"}


# ---------- Páginas web ----------
# Las páginas son plantillas; los datos se cargan desde la API con static/app.js.
PAGES = {
    "/": ("catalog.html", "Catálogo"),
    "/login": ("login.html", "Iniciar sesión"),
    "/registro": ("register.html", "Crear cuenta"),
    "/carrito": ("cart.html", "Carrito"),
    "/checkout": ("checkout.html", "Checkout"),
    "/ordenes": ("orders.html", "Mis órdenes"),
}


def page(template: str, title: str):
    def handler(request: Request):
        return templates.TemplateResponse(request, template, {"title": title})
    return handler


for path, (tpl, title) in PAGES.items():
    app.add_api_route(path, page(tpl, title), methods=["GET"], response_class=HTMLResponse, include_in_schema=False)


@app.get("/productos/{product_id}", response_class=HTMLResponse, include_in_schema=False)
def product_page(request: Request, product_id: int):
    return templates.TemplateResponse(request, "product.html", {"title": "Producto", "product_id": product_id})


@app.get("/pago/{order_id}", response_class=HTMLResponse, include_in_schema=False)
def payment_page(request: Request, order_id: int):
    return templates.TemplateResponse(request, "payment.html", {"title": "Pago", "order_id": order_id})


@app.get("/ordenes/{order_id}", response_class=HTMLResponse, include_in_schema=False)
def order_page(request: Request, order_id: int):
    return templates.TemplateResponse(request, "order_detail.html", {"title": "Orden", "order_id": order_id})
