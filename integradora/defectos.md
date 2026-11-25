# Reporte de defectos

| ID | Título | Severidad | Requisito | Estado | Prueba que lo detecta |
|---|---|---|---|---|---|
| BUG-01 | El detalle omite el aviso de últimas unidades con stock 0 | Baja | CA-05.2 | Abierto | `test_detalle_ultimas_unidades[0 unidades]` |
| BUG-02 | Una cuenta puede consultar el detalle de una orden ajena | Alta | CA-12.5 | Abierto | `test_detalle_ajeno_no_expone_orden` |
| BUG-03 | El código HTTP del login distingue cuentas existentes | Media | CA-02.2 | Abierto | `test_login_devuelve_error_generico` |
| BUG-04 | Un error de dirección expone datos personales | Alta | RNF-04 | Abierto | `test_errores_y_logs_omiten_datos_personales[direccion]` |
| BUG-05 | El carrito permite 11 unidades de un producto | Media | CA-06.2, RN-05 | Abierto | `test_carrito_rechaza_cantidad_fuera_de_rango[once]` |

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

## BUG-02 · Una cuenta puede consultar el detalle de una orden ajena

- **Requisito** · CA-12.5 impide ver o modificar órdenes de otros clientes.
- **Severidad alta** · La lectura indebida expone información de compra y dirección a otra cuenta.
- **Pasos** · Ejecutar `test_detalle_ajeno_no_expone_orden` con las dos cuentas sintéticas del laboratorio. Confirmar primero que el titular puede ver la orden y luego comprobar la denegación a la otra cuenta.
- **Esperado** · HTTP 404 con el mensaje de orden no encontrada y sin datos de la orden, según el contrato de detalle.
- **Obtenido** · HTTP 200. Se omite el contenido de la respuesta en este reporte.
- **Evidencia** · `test_detalle_ajeno_no_expone_orden` compara el 200 recibido con el 404 esperado y conserva el control del titular.

## BUG-03 · El código HTTP del login distingue cuentas existentes

- **Requisito** · CA-02.2 exige un error genérico que no indique si falló el correo o la contraseña.
- **Severidad media** · La diferencia revela si existe una cuenta. Las peticiones siguen sin autenticar al cliente.
- **Pasos** · Ejecutar `test_login_devuelve_error_generico`, que compara los dos rechazos sintéticos y comprueba que las credenciales válidas funcionan.
- **Esperado** · Mismo HTTP 401, definido en el contrato de login, y mismo cuerpo de error genérico en los dos rechazos.
- **Obtenido** · HTTP 404 para el correo inexistente y HTTP 401 para la contraseña incorrecta. Ambos cuerpos contienen únicamente el texto genérico.
- **Evidencia** · `test_login_devuelve_error_generico` conserva los dos códigos esperados y compara los cuerpos completos.

## BUG-04 · Un error de dirección expone datos personales

- **Requisito** · RNF-04 excluye correo, teléfono, dirección y datos de tarjeta de los mensajes de error y los logs.
- **Severidad alta** · Los logs retienen varios campos personales, y el mensaje de error reproduce el teléfono.
- **Pasos** · Ejecutar `test_errores_y_logs_omiten_datos_personales[direccion]` con la dirección sintética. Comprobar que se valida el código postal y revisar la salida de respuesta y logs por nombre de campo.
- **Esperado** · HTTP 400 con error de código postal. La respuesta y los logs omiten todos los valores personales.
- **Obtenido** · HTTP 400 con el teléfono en la respuesta. Los logs contienen correo, teléfono y componentes de la dirección.
- **Evidencia** · La prueba registra los nombres de los campos expuestos, sin incluir sus valores en el informe.

## BUG-05 · El carrito permite 11 unidades de un producto

- **Requisito** · CA-06.2 y RN-05 limitan el alta a 1–10 unidades y a las existencias disponibles.
- **Severidad media** · El carrito permite superar un límite de negocio y altera la cantidad del pedido.
- **Pasos** · Ejecutar `test_carrito_rechaza_cantidad_fuera_de_rango[once]` con el carrito vacío y un producto sintético que tenga 20 unidades.
- **Esperado** · HTTP 400 con el mensaje del rango permitido. El carrito sigue vacío.
- **Obtenido** · HTTP 200 para el alta de 11 unidades.
- **Evidencia** · `test_carrito_rechaza_cantidad_fuera_de_rango[once]` detecta el 200 recibido frente al 400 esperado. Los controles de 0 unidades y de exceso de stock se mantienen independientes.
