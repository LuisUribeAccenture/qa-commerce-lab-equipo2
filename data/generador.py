"""Generador de datos sintéticos para QA Commerce Lab (Lab 3.1).

Todos los datos son ficticios y reproducibles: la misma semilla produce siempre el mismo resultado.
"""
import random
import string
import unicodedata
from datetime import date

from faker import Faker

CATEGORIAS = ["Computación", "Audio", "Telefonía", "Hogar", "Accesorios"]
FECHA_REFERENCIA = date(2026, 11, 18)  # fija, para que las edades no cambien con el tiempo
DOMINIO = "example.com"  # dominio reservado para ejemplos: nunca es un correo real


def _faker(seed: int) -> tuple[Faker, random.Random]:
    fake = Faker("es_MX")
    fake.seed_instance(seed)
    return fake, random.Random(seed)


def _password(rng: random.Random) -> str:
    """Cumple RN-02: entre 8 y 64 caracteres, con al menos una letra y un número."""
    largo = rng.randint(8, 16)
    base = [rng.choice(string.ascii_letters), rng.choice(string.digits)]
    base += [rng.choice(string.ascii_letters + string.digits) for _ in range(largo - 2)]
    rng.shuffle(base)
    return "".join(base)


def _fecha_nacimiento(rng: random.Random, fecha_ref: date) -> str:
    """Edad entre 18 y 80 años cumplidos a la fecha de referencia (RN-03)."""
    edad = rng.randint(18, 80)
    anio = fecha_ref.year - edad
    mes = rng.randint(1, 12)
    dia = rng.randint(1, 28)
    nacimiento = date(anio, mes, dia)
    if nacimiento > date(anio, fecha_ref.month, min(fecha_ref.day, 28)):
        nacimiento = date(anio - 1, mes, dia)  # todavía no cumple años este año: un año más
    return nacimiento.isoformat()


def generar_clientes(n: int, seed: int = 42, fecha_ref: date = FECHA_REFERENCIA) -> list[dict]:
    fake, rng = _faker(seed)
    clientes = []
    for i in range(n):
        nombre = fake.first_name()
        apellido = fake.last_name()
        usuario = unicodedata.normalize("NFKD", f"{nombre}.{apellido}".lower()).encode("ascii", "ignore").decode()
        usuario = "".join(c for c in usuario if c.isalnum() or c == ".")
        email = f"{usuario}.{i}@{DOMINIO}"
        clientes.append({
            "name": f"{nombre} {apellido}",
            "email": email,
            "password": _password(rng),
            "birth_date": _fecha_nacimiento(rng, fecha_ref),
        })
    return clientes


def generar_productos(n: int, seed: int = 42) -> list[dict]:
    fake, rng = _faker(seed)
    productos = []
    for i in range(n):
        categoria = rng.choice(CATEGORIAS)
        productos.append({
            "name": f"Producto de prueba {i + 1} {fake.word().capitalize()}",
            "description": fake.sentence(nb_words=8),
            "price": round(rng.uniform(50, 30000), 2),
            "category": categoria,
            "stock": rng.choice([0, 1, 5, 6, 10, rng.randint(11, 100)]),
            "active": rng.random() > 0.1,
        })
    return productos


def generar_dataset(seed: int = 42, clientes: int = 10, productos: int = 20) -> dict:
    """Dataset en el formato que acepta POST /api/test/seed."""
    return {"users": generar_clientes(clientes, seed), "products": generar_productos(productos, seed)}


def cargar_en_app(dataset: dict, client) -> dict:
    """Carga el dataset en la app con /api/test/seed. `client` puede ser TestClient o requests.Session con base_url."""
    res = client.post("/api/test/seed", json=dataset)
    res.raise_for_status()
    return res.json()


if __name__ == "__main__":
    import json
    import sys

    semilla = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    print(json.dumps(generar_dataset(semilla), ensure_ascii=False, indent=2))
