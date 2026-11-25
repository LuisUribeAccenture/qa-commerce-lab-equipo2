---
name: revisar-pruebas
description: >
  Audita pruebas automatizadas existentes contra los requisitos del proyecto.
  Úsala cuando pidan revisar o auditar pruebas y sus oráculos. Solo lee y reporta.
  Las explicaciones de código de aplicación y la implementación de pruebas quedan fuera de su alcance.
---

# Revisar pruebas

1. Lee las pruebas indicadas, sus fixtures y `docs/requisitos.md`. Si se comprueba un contrato HTTP o un mock, consulta también el esquema o la documentación pertinente.
2. Relaciona cada aserción con un requisito o un contrato verificable. Si el resultado esperado es ambiguo, indica qué falta especificar. No uses la respuesta actual de la aplicación como oráculo.
3. Busca controles ausentes, aserciones que pueden pasar sin probar la conducta, oráculos copiados, esperas fijas, datos personales reales y mocks que sustituyan la regla o interfaz bajo prueba. Verifica que los cuerpos simulados respeten el esquema aplicable.
4. Entrega una tabla con un hallazgo comprobable por fila. Incluye la línea y cita el criterio exacto. Si la evidencia es insuficiente, indícalo sin atribuir un defecto. Omite las pruebas correctas.

| Prueba | Línea | Problema | Severidad | Requisito | Corrección |
|---|---:|---|---|---|---|

Trabaja en solo lectura. No modifiques archivos, no cambies aserciones y no ejecutes peticiones contra la aplicación para deducir resultados esperados. Tras entregar la tabla, espera.
