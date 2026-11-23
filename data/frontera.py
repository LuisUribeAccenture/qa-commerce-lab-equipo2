"""Datos de frontera e inválidos derivados de las reglas de negocio (Lab 3.2).

Cada función devuelve una lista de casos (valor, es_valido, descripción) para usar en
pruebas parametrizadas. Los casos salen del DOCUMENTO DE REQUISITOS, no del código de la app.

La primera función es el ejemplo. Agreguen las funciones de las reglas de SU ÁREA
(ver la guía del Lab 3.2) y sus pruebas en tests/data/test_frontera_api.py.
"""


def contrasenas() -> list[tuple[str, bool, str]]:
    """Ejemplo · RN-02: entre 8 y 64 caracteres, con al menos una letra y un número."""
    return [
        ("abc1234", False, "7 caracteres (debajo del mínimo)"),
        ("abcd1234", True, "8 caracteres (mínimo)"),
        ("a1" * 32, True, "64 caracteres (máximo)"),
        ("a1" * 32 + "b", False, "65 caracteres (arriba del máximo)"),
        ("abcdefgh", False, "solo letras"),
        ("12345678", False, "solo números"),
        ("", False, "vacía"),
    ]


def paginas() -> list[tuple[tuple[int, int, tuple[int, ...]], bool, str]]:
    """CA-03.2: ((productos activos, página inicial, tamaños esperados), petición válida, descripción)."""
    return [
        ((0, 1, (0,)), True, "sin productos activos"),
        ((19, 1, (19,)), True, "19 productos"),
        ((20, 1, (20,)), True, "20 productos"),
        ((21, 1, (20, 1)), True, "21 productos"),
        ((41, 1, (20, 20, 1)), True, "41 productos"),
        ((21, 0, ()), False, "página anterior a la primera"),
    ]


def existencias() -> list[tuple[int, bool, str]]:
    """CA-05.2: (existencias, debe mostrarse el aviso, descripción)."""
    return [
        (0, True, "0 unidades"),
        (1, True, "1 unidad"),
        (4, True, "4 unidades"),
        (5, True, "5 unidades"),
        (6, False, "6 unidades"),
    ]


def busquedas() -> list[tuple[str, bool, str]]:
    """CA-04.1: (consulta, hay coincidencia por nombre, descripción)."""
    return [
        ("Taza Frontera B", True, "nombre exacto"),
        ("Vaso Frontera B", False, "nombre inexistente"),
        ("Cerámica Frontera B", False, "texto solo en la descripción"),
    ]
