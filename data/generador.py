"""Generador de datos sintéticos para QA Commerce Lab (Lab 3.1).

Objetivo: que pasen todas las pruebas de tests/data/test_generador.py.
    pytest tests/data/test_generador.py

Reglas:
- Todos los datos son ficticios. Los correos usan el dominio example.com.
- Reproducible: la misma semilla produce siempre el mismo resultado (usa Faker.seed_instance
  y random.Random(seed); nunca el random global).
- Los datos válidos deben cumplir las reglas del documento de requisitos (RN-02, RN-03…).

Pueden pedir ayuda a Codex, pero revisen lo que genere: ¿respeta las reglas? ¿es reproducible?
"""
import random
from calendar import monthrange
from datetime import date

from faker import Faker

CATEGORIAS = ["Computación", "Audio", "Telefonía", "Hogar", "Accesorios"]
FECHA_REFERENCIA = date(2026, 11, 18)  # fija, para que las edades no cambien con el tiempo
DOMINIO = "example.com"  # dominio reservado para ejemplos: nunca es un correo real


def _faker(seed: int) -> tuple[Faker, random.Random]:
    fake = Faker("es_MX")
    fake.seed_instance(seed)
    return fake, random.Random(seed)


def generar_clientes(n: int, seed: int = 42, fecha_ref: date = FECHA_REFERENCIA) -> list[dict]:
    """Devuelve n clientes válidos: {"name", "email", "password", "birth_date"}.

    - email: único, con formato válido, solo ASCII y dominio example.com
    - password: cumple RN-02 (8 a 64 caracteres, al menos una letra y un número)
    - birth_date: AAAA-MM-DD, mayor de edad a fecha_ref (RN-03)
    """
    if n <= 0:
        return []
    if fecha_ref.year <= 18:
        raise ValueError("La fecha de referencia debe permitir una edad de al menos 18 años")

    anio_limite = fecha_ref.year - 18
    ultimo_dia = monthrange(anio_limite, fecha_ref.month)[1]
    fecha_limite = date(anio_limite, fecha_ref.month, min(fecha_ref.day, ultimo_dia))
    primer_dia = date(max(1, fecha_ref.year - 75), 1, 1).toordinal()
    dia_limite = fecha_limite.toordinal()

    fake, rng = _faker(seed)
    clientes = []
    for i in range(n):
        nombre = fake.name()
        email = f"cliente{i + 1}_{rng.randrange(10**9):09d}@{DOMINIO}"
        password = f"Qa{rng.randrange(10**12):012d}{rng.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}"
        nacimiento = date.fromordinal(rng.randint(primer_dia, dia_limite))
        clientes.append({
            "name": nombre,
            "email": email,
            "password": password,
            "birth_date": nacimiento.isoformat(),
        })
    return clientes


def generar_invalidos(seed: int) -> list[dict]:
    """Genera tres clientes con un único campo inválido en cada caso, a FECHA_REFERENCIA."""
    sin_numero, menor, correo_mal_formado = generar_clientes(3, seed)
    sin_numero["password"] = "SoloLetras"
    menor["birth_date"] = FECHA_REFERENCIA.isoformat()
    correo_mal_formado["email"] = correo_mal_formado["email"].replace("@", ".")
    return [sin_numero, menor, correo_mal_formado]


def generar_productos(n: int, seed: int = 42) -> list[dict]:
    """Devuelve n productos: {"name", "description", "price", "category", "stock", "active"}.

    - price: mayor que 0, con dos decimales
    - category: una de CATEGORIAS
    - stock: incluye casos de agotado (0), últimas unidades (1 a 5) y disponible (más de 5)
    """
    fake, rng = _faker(seed)
    productos = []
    for i in range(max(0, n)):
        categoria = rng.choice(CATEGORIAS)
        # Alternar los tres escenarios garantiza cobertura incluso con semillas distintas.
        tipo_stock = i % 3
        if tipo_stock == 0:
            stock = 0
        elif tipo_stock == 1:
            stock = rng.randint(1, 5)
        else:
            stock = rng.randint(6, 100)
        productos.append({
            "name": f"{categoria} {fake.word().capitalize()} {i + 1}",
            "description": fake.sentence(),
            "price": rng.randint(1, 500000) / 100,
            "category": categoria,
            "stock": stock,
            "active": rng.choice([True, True, True, False]),
        })
    return productos


def generar_dataset(seed: int = 42, clientes: int = 10, productos: int = 20) -> dict:
    """Dataset en el formato que acepta POST /api/test/seed: {"users": [...], "products": [...]}."""
    return {"users": generar_clientes(clientes, seed), "products": generar_productos(productos, seed)}


def cargar_en_app(dataset: dict, client) -> dict:
    """Carga el dataset en la app con POST /api/test/seed y devuelve los IDs creados."""
    res = client.post("/api/test/seed", json=dataset)
    res.raise_for_status()
    return res.json()


if __name__ == "__main__":
    import json
    import sys

    semilla = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    print(json.dumps(generar_dataset(semilla), ensure_ascii=False, indent=2))
