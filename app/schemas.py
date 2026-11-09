"""Modelos de entrada y salida de la API. Definen el contrato OpenAPI publicado en /openapi.json."""
from pydantic import BaseModel, Field


class ErrorOut(BaseModel):
    detail: str
    errors: dict[str, str] | None = None


# ---------- Autenticación ----------
class RegisterIn(BaseModel):
    name: str = ""
    email: str = ""
    password: str = ""
    password_confirm: str = ""
    birth_date: str = Field("", description="Fecha en formato AAAA-MM-DD")


class LoginIn(BaseModel):
    email: str = ""
    password: str = ""


class Address(BaseModel):
    street: str = ""
    neighborhood: str = ""
    city: str = ""
    state: str = ""
    postal_code: str = ""
    phone: str = ""


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    saved_address: Address | None = None


class AuthOut(BaseModel):
    token: str
    user: UserOut


# ---------- Catálogo ----------
class Category(BaseModel):
    id: int
    name: str


class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    category_id: int
    stock: int
    available: bool
    low_stock: bool
    image: str


class ProductPage(BaseModel):
    items: list[ProductOut]
    page: int
    page_size: int
    total: int


# ---------- Carrito ----------
class CartItemIn(BaseModel):
    product_id: int
    quantity: int = 1


class CartQuantityIn(BaseModel):
    quantity: int


class CouponIn(BaseModel):
    code: str = ""


class CartItemOut(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int
    line_total: float
    stock: int
    image: str


class CartOut(BaseModel):
    items: list[CartItemOut]
    item_count: int
    subtotal: float
    discount: float
    shipping: float
    total: float
    coupon_code: str | None


# ---------- Órdenes ----------
class OrderIn(BaseModel):
    address: Address
    save_address: bool = False


class PaymentIn(BaseModel):
    card_holder: str = ""
    card_number: str = ""
    expiry: str = Field("", description="Formato MM/AA")
    cvv: str = ""


class OrderItemOut(BaseModel):
    product_id: int
    name: str
    unit_price: float
    quantity: int


class OrderOut(BaseModel):
    id: int
    status: str
    subtotal: float
    discount: float
    shipping: float
    total: float
    coupon_code: str | None
    address: Address
    card_last4: str | None
    created_at: str
    paid_at: str | None
    items: list[OrderItemOut]


class OrderSummary(BaseModel):
    id: int
    status: str
    total: float
    created_at: str
