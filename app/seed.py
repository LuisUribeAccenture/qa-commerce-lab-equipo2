"""Datos base deterministas: siempre se cargan los mismos productos, usuarios y cupones."""
import json
from datetime import datetime, timedelta

from app.security import hash_password

CATEGORIES = ["Computación", "Audio", "Telefonía", "Hogar", "Accesorios"]

# (nombre, descripción, precio, categoría, stock, activo)
PRODUCTS = [
    ("Laptop Nébula 14", "Laptop ligera de 14 pulgadas, 16 GB RAM, 512 GB SSD.", 18999.00, "Computación", 12, 1),
    ("Laptop Titán 16", "Laptop para alto rendimiento, 32 GB RAM, 1 TB SSD.", 32499.00, "Computación", 4, 1),
    ("Monitor Panorámico 27", "Monitor IPS 27 pulgadas, resolución QHD.", 5499.00, "Computación", 20, 1),
    ("Teclado Mecánico Kappa", "Teclado mecánico con switches táctiles.", 1299.00, "Computación", 35, 1),
    ("Mouse Inalámbrico Orbit", "Mouse ergonómico con batería recargable.", 499.50, "Computación", 50, 1),
    ("Disco SSD Externo 1 TB", "Almacenamiento portátil USB-C.", 1899.00, "Computación", 0, 1),
    ("Webcam Full HD Lumen", "Cámara 1080p con micrófono integrado.", 899.00, "Computación", 18, 1),
    ("Hub USB-C 7 en 1", "HDMI, USB-A, lector SD y carga PD.", 749.00, "Computación", 3, 1),
    ("Audífonos Pro ANC", "Audífonos inalámbricos con cancelación de ruido.", 3999.00, "Audio", 25, 1),
    ("Audífonos Deportivos Pulse", "Resistentes al sudor, 8 h de batería.", 999.00, "Audio", 40, 1),
    ("Bocina Portátil Wave", "Bocina Bluetooth resistente al agua.", 1499.00, "Audio", 22, 1),
    ("Barra de Sonido Cinema", "Barra de sonido 2.1 con subwoofer.", 4299.00, "Audio", 7, 1),
    ("Micrófono USB Podcast", "Micrófono de condensador para streaming.", 1599.00, "Audio", 0, 1),
    ("Tocadiscos Retro", "Tocadiscos con bocinas integradas.", 2799.00, "Audio", 5, 1),
    ("Audífonos Básicos con Cable", "Audífonos de 3.5 mm.", 199.00, "Audio", 100, 1),
    ("Smartphone Astro X", "Pantalla 6.5 pulgadas, 256 GB.", 12999.00, "Telefonía", 15, 1),
    ("Smartphone Astro Lite", "Pantalla 6.1 pulgadas, 128 GB.", 6999.00, "Telefonía", 30, 1),
    ("Funda Antigolpes Astro", "Funda de silicón reforzada.", 333.00, "Telefonía", 60, 1),
    ("Cargador Rápido 30 W", "Cargador USB-C con carga rápida.", 449.00, "Telefonía", 45, 1),
    ("Mica de Cristal Templado", "Protector de pantalla 9H.", 149.00, "Telefonía", 80, 1),
    ("Smartwatch Fit 2", "Monitor de ritmo cardiaco y GPS.", 2999.00, "Telefonía", 2, 1),
    ("Power Bank 20000 mAh", "Batería portátil con dos salidas.", 699.00, "Telefonía", 28, 1),
    ("Cafetera Express Aroma", "Cafetera de 15 bares con espumador.", 3499.00, "Hogar", 9, 1),
    ("Aspiradora Robot Clean", "Aspiradora automática con mapeo.", 5999.00, "Hogar", 6, 1),
    ("Foco Inteligente RGB", "Foco Wi-Fi compatible con asistentes de voz.", 249.00, "Hogar", 70, 1),
    ("Enchufe Inteligente", "Controla aparatos desde el celular.", 299.00, "Hogar", 55, 1),
    ("Purificador de Aire Brisa", "Filtro HEPA para espacios de 30 m².", 2499.00, "Hogar", 11, 1),
    ("Báscula Digital de Cocina", "Precisión de 1 g, hasta 5 kg.", 349.00, "Hogar", 0, 1),
    ("Freidora de Aire 4 L", "Freidora sin aceite con 8 programas.", 1799.00, "Hogar", 14, 1),
    ("Lámpara de Escritorio LED", "Tres tonos de luz y brillo ajustable.", 599.00, "Hogar", 1, 1),
    ("Mochila para Laptop Urban", "Compartimento acolchado de 15.6 pulgadas.", 899.00, "Accesorios", 33, 1),
    ("Base Refrigerante para Laptop", "Dos ventiladores silenciosos.", 459.00, "Accesorios", 19, 1),
    ("Cable HDMI 2 m", "Compatible con 4K a 60 Hz.", 179.00, "Accesorios", 90, 1),
    ("Soporte para Celular", "Soporte de escritorio ajustable.", 229.00, "Accesorios", 48, 1),
    ("Tapete para Mouse XL", "Tapete de 90 × 40 cm.", 329.00, "Accesorios", 37, 1),
    ("Organizador de Cables", "Kit de 20 cintas reutilizables.", 129.00, "Accesorios", 0, 1),
    ("Adaptador de Viaje Universal", "Compatible con más de 150 países.", 389.00, "Accesorios", 26, 1),
    ("Funda para Tablet 11", "Funda con soporte y espacio para lápiz.", 549.00, "Accesorios", 4, 1),
    # Inactivos: no deben aparecer en el catálogo (CA-03.4)
    ("Reproductor MP3 Clásico", "Producto descontinuado.", 599.00, "Audio", 10, 0),
    ("Laptop Nébula 13 (2023)", "Modelo anterior descontinuado.", 14999.00, "Computación", 3, 0),
]

COUPONS = [
    # (código, tipo, valor, subtotal mínimo, solo primera compra, válido hasta)
    ("BIENVENIDA10", "percent", 10, 0, 1, None),
    ("ENVIOGRATIS", "shipping", 0, 500, 0, None),
    ("AHORRA200", "fixed", 200, 1500, 0, None),
    ("NAVIDAD25", "percent", 25, 0, 0, "2025-12-31"),
]

# Contraseña de todos los usuarios de ejemplo: Password123
USERS = [
    ("Ana García", "ana.garcia@example.com", "1990-04-12"),
    ("Luis Pérez", "luis.perez@example.com", "1985-09-30"),
]

LUIS_ADDRESS = {
    "street": "Av. Siempre Viva 742", "neighborhood": "Centro", "city": "Monterrey",
    "state": "Nuevo León", "postal_code": "64000", "phone": "8112345678",
}


def seed_base(conn) -> None:
    for i, name in enumerate(CATEGORIES, start=1):
        conn.execute("INSERT INTO categories (id, name) VALUES (?, ?)", (i, name))
    cat_ids = {name: i for i, name in enumerate(CATEGORIES, start=1)}
    for idx, (name, desc, price, cat, stock, active) in enumerate(PRODUCTS, start=1):
        conn.execute(
            "INSERT INTO products (name, description, price, category_id, stock, active, image) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, desc, price, cat_ids[cat], stock, active, f"/static/img/{cat_ids[cat]}.svg"))
    for c in COUPONS:
        conn.execute("INSERT INTO coupons VALUES (?, ?, ?, ?, ?, ?)", c)
    created = datetime(2026, 1, 1).isoformat()
    for name, email, birth in USERS:
        conn.execute(
            "INSERT INTO users (name, email, password_hash, birth_date, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, email, hash_password("Password123"), birth, created))
    # Luis tiene una orden pagada (la orden 1)
    paid = (datetime.now() - timedelta(days=3)).isoformat()
    conn.execute(
        "INSERT INTO orders (user_id, status, subtotal, discount, shipping, total, coupon_code, address, "
        "card_last4, created_at, paid_at) VALUES (2, 'Pagada', 3999.00, 0, 0, 3999.00, NULL, ?, '1111', ?, ?)",
        (json.dumps(LUIS_ADDRESS), paid, paid))
    conn.execute("INSERT INTO order_items VALUES (1, 9, 'Audífonos Pro ANC', 3999.00, 1)")
    conn.execute("UPDATE users SET saved_address = ? WHERE id = 2", (json.dumps(LUIS_ADDRESS),))
