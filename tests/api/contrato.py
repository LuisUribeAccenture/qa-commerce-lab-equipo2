"""Validación de respuestas contra los esquemas del contrato OpenAPI.

Uso en una prueba:
    from tests.api.contrato import validar
    validar(contrato, "ProductPage", res.json())

Si la respuesta no cumple el esquema, lanza jsonschema.ValidationError con el detalle.
"""
from jsonschema import Draft202012Validator


def validar(contrato: dict, esquema: str, datos) -> None:
    schema = {"$ref": f"#/components/schemas/{esquema}", "components": contrato["components"]}
    Draft202012Validator(schema).validate(datos)
