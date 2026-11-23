# Reporte de defectos

| ID | Título | Severidad | Requisito | Estado | Prueba que lo detecta |
|---|---|---|---|---|---|
| BUG-01 | El detalle omite el aviso de últimas unidades con stock 0 | Baja | CA-05.2 | Abierto | `test_detalle_ultimas_unidades[0 unidades]` |

## BUG-01 · El detalle omite el aviso de últimas unidades con stock 0

- **Requisito:** CA-05.2 pide el aviso «¡Últimas unidades!» para 5 unidades o menos.
- **Severidad:** Baja. Viaja el stock correcto y el producto agotado sigue sin poder agregarse desde el detalle. El impacto es el aviso omitido.
- **Entorno:** API local de QA Commerce Lab, rama `equipo-2`, Python 3.14 y pytest 9.2.
- **Datos de prueba:** producto activo «Taza Frontera B», precio 100 y stock 0.

### Pasos para reproducir

1. Crear el producto con `POST /api/test/seed` y guardar su ID.
2. Consultar `GET /api/products/{id}` y leer `stock`, `available` y `low_stock`.

**Resultado esperado según el texto de CA-05.2**

HTTP 200, `stock: 0`, `available: false` y `low_stock: true`. El texto del criterio incluye el 0 y no especifica una excepción en el detalle.

**Resultado obtenido**

HTTP 200 con `{"stock": 0, "available": false, "low_stock": false}`. El detalle web usa `low_stock` para decidir si muestra el aviso.

**Evidencia**

El caso falló en la primera ejecución parametrizada y se reprodujo con una consulta independiente. En esa segunda verificación, 1, 4 y 5 devolvieron `low_stock: true` y 6 devolvió `false`. El caso de 0 queda marcado con `xfail(strict=True)`. Se puede reproducir sin la marca con `pytest tests/data/test_frontera_api.py -k "detalle and 0" --runxfail -v`.
