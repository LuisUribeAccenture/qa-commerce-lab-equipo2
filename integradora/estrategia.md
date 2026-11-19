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