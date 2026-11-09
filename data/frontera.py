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


# TODO: agreguen aquí las funciones de su área. Ideas:
#   Área A: fechas_nacimiento() (RN-03)
#   Área B: busquedas() (CA-04.1), paginas() (CA-03.2)
#   Área C: cantidades() (RN-05), subtotales_envio() (RN-08)
#   Área D: codigos_postales() y telefonos() (CA-10.2), tarjetas() (CA-11.2)
#   Área E: horas_desde_pago() (RN-09)
