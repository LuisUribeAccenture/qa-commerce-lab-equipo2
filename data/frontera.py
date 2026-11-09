"""Datos de frontera e inválidos derivados de las reglas de negocio (Lab 3.2).

Cada función devuelve una lista de casos (valor, es_valido, descripción) para usar en
pruebas parametrizadas. Los casos salen del documento de requisitos, no de la implementación.
"""
from datetime import date, timedelta


def _menos_anios(ref: date, anios: int) -> date:
    try:
        return ref.replace(year=ref.year - anios)
    except ValueError:  # 29 de febrero
        return ref.replace(year=ref.year - anios, day=28)


def contrasenas() -> list[tuple[str, bool, str]]:
    """RN-02: entre 8 y 64 caracteres, con al menos una letra y un número."""
    return [
        ("abc1234", False, "7 caracteres (debajo del mínimo)"),
        ("abcd1234", True, "8 caracteres (mínimo)"),
        ("a1" * 32, True, "64 caracteres (máximo)"),
        ("a1" * 32 + "b", False, "65 caracteres (arriba del máximo)"),
        ("abcdefgh", False, "solo letras"),
        ("12345678", False, "solo números"),
        ("", False, "vacía"),
    ]


def fechas_nacimiento(ref: date | None = None) -> list[tuple[str, bool, str]]:
    """RN-03: 18 años cumplidos a la fecha de registro."""
    ref = ref or date.today()
    cumple_18_hoy = _menos_anios(ref, 18)
    return [
        (cumple_18_hoy.isoformat(), True, "cumple 18 años hoy"),
        ((cumple_18_hoy + timedelta(days=1)).isoformat(), False, "cumple 18 años mañana"),
        ((cumple_18_hoy - timedelta(days=1)).isoformat(), True, "cumplió 18 años ayer"),
        (ref.isoformat(), False, "nació hoy"),
        ("2000-02-30", False, "fecha inexistente"),
        ("", False, "vacía"),
    ]


def cantidades() -> list[tuple[int, bool, str]]:
    """RN-05: entre 1 y 10 unidades del mismo producto."""
    return [
        (0, False, "debajo del mínimo"),
        (1, True, "mínimo"),
        (2, True, "mínimo + 1"),
        (9, True, "máximo - 1"),
        (10, True, "máximo"),
        (11, False, "máximo + 1"),
        (-1, False, "negativa"),
    ]


def codigos_postales() -> list[tuple[str, bool, str]]:
    """CA-10.2: 5 dígitos."""
    return [("6400", False, "4 dígitos"), ("64000", True, "5 dígitos"), ("640000", False, "6 dígitos"),
            ("64a00", False, "con letra"), ("", False, "vacío")]


def telefonos() -> list[tuple[str, bool, str]]:
    """CA-10.2: 10 dígitos."""
    return [("811234567", False, "9 dígitos"), ("8112345678", True, "10 dígitos"),
            ("81123456789", False, "11 dígitos"), ("81-1234-567", False, "con guiones")]
