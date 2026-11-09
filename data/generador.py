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
    raise NotImplementedError


def generar_productos(n: int, seed: int = 42) -> list[dict]:
    """Devuelve n productos: {"name", "description", "price", "category", "stock", "active"}.

    - price: mayor que 0, con dos decimales
    - category: una de CATEGORIAS
    - stock: incluye casos de agotado (0), últimas unidades (1 a 5) y disponible (más de 5)
    """
    raise NotImplementedError


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
