"""Acceso a la base de datos SQLite."""
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.environ.get("QACL_DB", Path(__file__).resolve().parent.parent / "qa_commerce.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TEXT,
    saved_address TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    last_seen TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    price REAL NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    stock INTEGER NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    image TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS carts (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    coupon_code TEXT
);
CREATE TABLE IF NOT EXISTS cart_items (
    user_id INTEGER NOT NULL REFERENCES users(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    PRIMARY KEY (user_id, product_id)
);
CREATE TABLE IF NOT EXISTS coupons (
    code TEXT PRIMARY KEY,
    kind TEXT NOT NULL,            -- percent | fixed | shipping
    value REAL NOT NULL,
    min_subtotal REAL NOT NULL DEFAULT 0,
    first_purchase_only INTEGER NOT NULL DEFAULT 0,
    valid_until TEXT
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    status TEXT NOT NULL,
    subtotal REAL NOT NULL,
    discount REAL NOT NULL,
    shipping REAL NOT NULL,
    total REAL NOT NULL,
    coupon_code TEXT,
    address TEXT NOT NULL,
    card_last4 TEXT,
    created_at TEXT NOT NULL,
    paid_at TEXT
);
CREATE TABLE IF NOT EXISTS order_items (
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    name TEXT NOT NULL,
    unit_price REAL NOT NULL,
    quantity INTEGER NOT NULL
);
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db():
    """Dependencia de FastAPI: una conexión por petición."""
    conn = connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(reset: bool = False) -> None:
    from app.seed import seed_base

    conn = connect()
    try:
        if reset:
            tables = [r["name"] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
            conn.execute("PRAGMA foreign_keys = OFF")
            for t in tables:
                conn.execute(f"DROP TABLE IF EXISTS {t}")
            conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
            seed_base(conn)
        conn.commit()
    finally:
        conn.close()
