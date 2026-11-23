---
name: refactor-web-page-objects
description: Refactoriza pruebas web existentes de pytest y Playwright al patrón Page Object y verifica que la suite nueva conserve el comportamiento de la original.
---

# Refactorizar pruebas web con Page Objects

## Línea base y equivalencia

1. Identifica la suite original y solicita su línea base si ya se midió. Antes de editar, ejecuta la suite original con `pytest <ruta-original> --durations=0`. Registra el comando, el navegador, los resultados y los tiempos. Distingue los fallos preexistentes de las regresiones del refactor.
2. Haz un mapa de cada aserción original a su equivalente en la suite nueva. Registra el escenario, el resultado esperado y su origen. Conserva las precondiciones, los datos, las comprobaciones negativas y el sentido de cada comparación, incluida la diferencia entre texto exacto y texto parcial.

## Refactorización

- Crea la suite nueva en paralelo y conserva la aplicación, los fixtures y la suite original. Reutiliza los fixtures existentes para mantener el aislamiento de las pruebas.
- Encapsula los localizadores y las acciones reutilizables en Page Objects que reciban el fixture `page`. Mantén el flujo del escenario y sus aserciones de negocio visibles en la prueba.
- Prefiere `get_by_role()` con nombre accesible y `get_by_label()`. Si la interfaz carece de un nombre o etiqueta adecuados, usa un identificador estable disponible. Evita selectores ligados a la jerarquía del HTML, como `form > button`, y posiciones como `nth()` usadas solo para distinguir elementos.
- Sustituye las esperas fijas, como `time.sleep()` y `wait_for_timeout()`, por el autoesperado de Playwright o por una condición observable. Usa `expect` para verificar esa condición y para reemplazar las comparaciones inmediatas con `inner_text()`. Elige una aserción que conserve la intención original, como `to_have_text()` para texto exacto o `to_contain_text()` para texto parcial.

## Validación

1. Ejecuta por separado la suite original y la refactorizada con condiciones comparables. Registra los comandos, los resultados y las duraciones de ambas. Comprueba que el mapa cubra todas las aserciones originales.
2. Propón retirar la suite original solo si ambas ejecuciones pasan y la equivalencia está verificada. Si queda algún fallo o alguna aserción sin equivalencia, indícalo junto con la evidencia. Conserva la suite original hasta que exista una autorización explícita para retirarla.