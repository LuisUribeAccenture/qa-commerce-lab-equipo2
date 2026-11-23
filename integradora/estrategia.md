Característica: Consulta del catálogo (HU-03)

@HU-03 @CA-03.1
Escenario: Mostrar los cuatro datos de un producto activo
Dado que "Taza" está activa, tiene imagen, precio 120 y 8 existencias
Cuando un visitante consulta el catálogo
Entonces "Taza" aparece con imagen, nombre "Taza", precio 120 y un dato de disponibilidad visible

@HU-03 @CA-03.2
Esquema del escenario: Paginar productos activos en grupos de 20
Dado que existen <total> productos activos
Cuando se consulta el catálogo
Entonces la primera página contiene <primera> productos
Y la página <ultima_pagina> contiene <ultima_cantidad> productos

Ejemplos:
| total | primera | ultima_pagina | ultima_cantidad |
| 20    | 20      | 1             | 20              |
| 21    | 20      | 2             | 1               |
| 41    | 20      | 3             | 1               |

@HU-03 @CA-03.3
Escenario: Marcar como agotado un producto sin stock
Dado que "Taza" está activa y tiene 0 existencias
Cuando un visitante consulta el catálogo
Entonces "Taza" muestra la etiqueta exacta "Agotado"

@HU-03 @CA-03.3
Escenario: Impedir agregar un producto agotado
Dado que "Taza" tiene 0 existencias y el carrito no contiene "Taza"
Cuando el visitante intenta agregar "Taza" al carrito
Entonces la cantidad de "Taza" en el carrito permanece en 0

@HU-03 @CA-03.4
Escenario: Excluir productos inactivos del catálogo
Dado que "Taza" está activa y "Jarra" está inactiva
Cuando un visitante consulta el catálogo
Entonces "Taza" aparece una vez y "Jarra" aparece 0 veces

5.2. HU-04 · Búsqueda y filtrado

Característica: Búsqueda y filtrado de productos (HU-04)

@HU-04 @CA-04.1
Escenario: Buscar un producto por su nombre exacto
Dado que existe un producto activo llamado "Taza"
Cuando el visitante busca el nombre "Taza"
Entonces los resultados incluyen el producto llamado "Taza"

@HU-04 @CA-04.2
Escenario: Filtrar productos por una categoría
Dado que "Taza" pertenece a "Hogar" y "Balón" a "Deportes"
Cuando el visitante filtra por "Hogar"
Entonces se muestra "Taza" y no se muestra "Balón"

@HU-04 @CA-04.3
Esquema del escenario: Ordenar productos por precio
Dado que hay tres productos con precios 10, 20 y 30
Cuando el visitante elige el orden "<orden>"
Entonces la lista de precios es "<secuencia>"

Ejemplos:
| orden        | secuencia  |
| ascendente   | 10, 20, 30 |
| descendente  | 30, 20, 10 |

@HU-04 @CA-04.1 @CA-04.2 @CA-04.3 @CA-04.4
Escenario: Combinar búsqueda, categoría y orden
Dado que existen "Tenis" en "Calzado" a 150 y 90
Y existe "Tenis" en "Hogar" a 50 y "Gorra" en "Calzado" a 60
Cuando el visitante busca "Tenis", filtra "Calzado" y ordena ascendente
Entonces aparecen exactamente 2 productos con precios 90 y 150, en ese orden

@HU-04 @CA-04.5
Escenario: Informar cuando la búsqueda no tiene resultados
Dado que no existe ningún producto llamado "ProductoInexistente"
Cuando el visitante busca "ProductoInexistente"
Entonces aparece el texto exacto "No encontramos productos para tu búsqueda"

5.3. HU-05 · Detalle de producto y cantidad

Característica: Detalle de producto (HU-05)

@HU-05 @CA-05.1
Escenario: Mostrar los seis datos del detalle
Dado que "Taza" tiene descripción "Cerámica", precio 120,
Y pertenece a "Hogar", tiene una imagen y 8 existencias
Cuando el visitante consulta el detalle de "Taza"
Entonces se muestran nombre "Taza", descripción "Cerámica", precio 120,
Y categoría "Hogar", al menos una imagen y 8 existencias

@HU-05 @CA-05.2
Esquema del escenario: Avisar de últimas unidades
Dado que "Taza" tiene <stock> existencias
Cuando el visitante consulta el detalle de "Taza"
Entonces aparece el texto exacto "¡Últimas unidades!"

Ejemplos:
| stock |
| 1     |
| 5     |

@HU-05 @CA-05.3 @ReglaNegocio2
Esquema del escenario: Agregar una cantidad permitida al carrito
Dado que "Taza" tiene 10 existencias y hay 0 unidades en el carrito
Cuando el visitante agrega <cantidad> unidades de "Taza" desde el detalle
Entonces el carrito contiene <cantidad> unidades de "Taza"

Ejemplos:
| cantidad |
| 1        |
| 10       |

@HU-05 @ReglaNegocio2
Esquema del escenario: Evitar cantidades de carrito fuera de 1 a 10
Dado que "Taza" tiene 20 existencias y hay 0 unidades en el carrito
Cuando el visitante intenta agregar <cantidad> unidades de "Taza"
Entonces no existe una línea de "Taza" con <cantidad> unidades en el carrito

Ejemplos:
| cantidad |
| 0        |
| 11       |

@HU-05 @ReglaNegocio2
Escenario: No superar las existencias disponibles
Dado que "Taza" tiene 5 existencias y hay 0 unidades en el carrito
Cuando el visitante intenta agregar 6 unidades de "Taza"
Entonces el carrito no contiene 6 unidades de "Taza"

## Datos de frontera del área B · Catálogo

Se derivaron los casos de [los requisitos](../docs/requisitos.md) y de los escenarios de catálogo, búsqueda y detalle anteriores. En la primera revisión se comprobó el resultado esperado contra el criterio. En la segunda se contrastó con las respuestas de la API, manteniendo el mismo resultado esperado.

| Regla | Valor | ¿Válido? | Resultado esperado según el requisito | Resultado de la API |
|---|---|---|---|---|
| CA-03.2 y CA-03.4 | 0, 19 o 20 productos activos | Sí | Una página con 0, 19 o 20 resultados, respectivamente. El producto inactivo no se cuenta ni aparece. | Coincide |
| CA-03.2 y CA-03.4 | 21 productos activos | Sí | Páginas de 20 y 1. Cada producto activo aparece una sola vez. | Coincide |
| CA-03.2 y CA-03.4 | 41 productos activos | Sí | Páginas de 20, 20 y 1. Se recuperan los 41 productos activos sin duplicados. | Coincide |
| CA-03.2 y contrato de la API | Página 0 con 21 productos activos | No | El contrato de la API empieza en la página 1 y rechaza 0 con HTTP 422. | Coincide |
| CA-05.2 | 0 unidades | Sí | HTTP 200 y `low_stock: true` según «5 unidades o menos». | HTTP 200, `low_stock: false` (BUG-01) |
| CA-05.2 | 1, 4 o 5 unidades | Sí | HTTP 200 y `low_stock: true`. | Coincide |
| CA-05.2 | 6 unidades | Sí | HTTP 200 y `low_stock: false`. | Coincide |
| CA-04.1 | `Taza Frontera B` | Sí | Devuelve el producto con ese nombre. | Coincide |
| CA-04.1 | `Vaso Frontera B` | Sí | Devuelve una lista vacía. El nombre no existe. | Coincide |
| CA-04.1 | `Cerámica Frontera B` | Sí | Devuelve una lista vacía. El texto solo aparece en la descripción. | Coincide |

La paginación usa un nombre común para aislar los productos de prueba y compara sus IDs con los resultados de todas las páginas. En búsqueda, una petición válida puede producir cero coincidencias. Para CA-05.2 la API se verifica mediante `low_stock`, el campo que utiliza el detalle web para mostrar «¡Últimas unidades!». CA-03.3 prescribe «Agotado» en el catálogo y CA-05.2 no indica una excepción para 0 en el detalle.

### Desafío de registro

`generar_invalidos(42)` modifica un solo campo de cada cliente base y conserva la confirmación de la contraseña al enviar la solicitud. Se verificó que la misma semilla repite los datos, que la semilla 43 los cambia y que los tres clientes base reciben HTTP 201 al registrarse.

| Regla | Valor inválido | ¿Válido? | Resultado esperado | Resultado de la API |
|---|---|---|---|---|
| RN-02 | `SoloLetras`, de longitud válida, sin dígitos | No | HTTP 400, error en `password`. | Coincide |
| RN-03 | Nacimiento el 2026-11-18, fecha de referencia del generador | No | HTTP 400, error en `birth_date`. | Coincide |
| CA-01.3 | Correo sintético sin `@` | No | HTTP 400, error en `email`. | Coincide |

Para que el caso de edad siga siendo reproducible, la prueba de registro usa la misma fecha de referencia que el generador. Las tres variantes devuelven únicamente el error del campo mutado y ninguna entrega un token.

### Resultado de ejecución

Las dos ejecuciones completas de `pytest tests/data` recolectaron 33 casos. Ambas terminaron con 32 aprobados y 1 fallo esperado (BUG-01).
