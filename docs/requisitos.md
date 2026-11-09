# QA Commerce Lab — Documento de requisitos

**Versión:** 1.0 · **Estado:** aprobado para pruebas · **Producto:** tienda en línea ficticia de artículos de tecnología y hogar

> Sistema creado exclusivamente para fines de capacitación. Todos los datos son ficticios.

---

## 1. Descripción general

QA Commerce Lab es una tienda en línea donde los clientes pueden registrarse, consultar un catálogo, armar un carrito, aplicar cupones de descuento y pagar sus compras con un medio de pago simulado. El sistema tiene tres componentes:

- **Aplicación web**, para navegadores de escritorio y móviles.
- **Aplicación móvil**, que ofrece las mismas funciones de compra que la web.
- **API REST**, que usan la web y la app móvil. Su contrato está publicado en formato OpenAPI.

Las reglas de negocio de este documento aplican por igual a la web, a la app móvil y a la API.

### 1.1 Roles

| Rol | Descripción |
|---|---|
| Visitante | Persona no autenticada. Puede consultar el catálogo. |
| Cliente | Persona registrada y autenticada. Puede comprar y consultar sus órdenes. |

### 1.2 Convenciones

- Los precios están en pesos mexicanos (MXN), con dos decimales.
- **HU** = historia de usuario · **CA** = criterio de aceptación · **RN** = regla de negocio · **RNF** = requisito no funcional.

---

## 2. Historias de usuario

### HU-01 · Registro de cliente

**Como** visitante **quiero** crear una cuenta **para** poder comprar en la tienda.

**Criterios de aceptación**

- **CA-01.1** El formulario pide: nombre completo, correo electrónico, contraseña, confirmación de contraseña y fecha de nacimiento.
- **CA-01.2** Todos los campos son obligatorios.
- **CA-01.3** El correo debe tener un formato válido y no puede estar registrado previamente (RN-01).
- **CA-01.4** La contraseña debe cumplir la política de contraseñas (RN-02), y la confirmación debe coincidir con ella.
- **CA-01.5** El cliente debe ser mayor de edad (RN-03).
- **CA-01.6** Si el registro es exitoso, el cliente queda autenticado y ve la página principal con el mensaje "Bienvenido, {nombre}".
- **CA-01.7** Si hay errores, se muestra un mensaje junto a cada campo inválido y no se pierden los datos ya capturados, excepto las contraseñas.

### HU-02 · Inicio de sesión

**Como** cliente **quiero** iniciar sesión con mi correo y contraseña **para** acceder a mi cuenta.

**Criterios de aceptación**

- **CA-02.1** Con credenciales correctas, el cliente queda autenticado y ve la página principal.
- **CA-02.2** Con credenciales incorrectas, se muestra el mensaje genérico "Correo o contraseña incorrectos", sin indicar cuál de los dos falló.
- **CA-02.3** Después de 5 intentos fallidos consecutivos, la cuenta se bloquea durante 15 minutos (RN-04).
- **CA-02.4** Mientras la cuenta está bloqueada, se muestra "Cuenta bloqueada temporalmente. Intenta más tarde.", aunque la contraseña sea correcta.
- **CA-02.5** La sesión expira después de 30 minutos de inactividad.

### HU-03 · Consulta del catálogo

**Como** visitante o cliente **quiero** ver los productos disponibles **para** elegir qué comprar.

**Criterios de aceptación**

- **CA-03.1** El catálogo muestra por cada producto: imagen, nombre, precio y disponibilidad.
- **CA-03.2** Los productos se muestran en páginas de 20.
- **CA-03.3** Un producto sin existencias se muestra con la etiqueta "Agotado" y no se puede agregar al carrito.
- **CA-03.4** Los productos inactivos no aparecen en el catálogo.

### HU-04 · Búsqueda y filtrado de productos

**Como** visitante o cliente **quiero** buscar y filtrar productos **para** encontrar rápidamente lo que necesito.

**Criterios de aceptación**

- **CA-04.1** Existe un campo de búsqueda por nombre de producto.
- **CA-04.2** Se puede filtrar por una categoría (ver sección 4.1).
- **CA-04.3** Se puede ordenar por precio, ascendente o descendente.
- **CA-04.4** La búsqueda, el filtro y el orden se pueden combinar.
- **CA-04.5** Si no hay resultados, se muestra "No encontramos productos para tu búsqueda".

### HU-05 · Detalle de producto

**Como** visitante o cliente **quiero** ver el detalle de un producto **para** decidir si lo compro.

**Criterios de aceptación**

- **CA-05.1** El detalle muestra: nombre, descripción, precio, categoría, imágenes y existencias disponibles.
- **CA-05.2** Si quedan 5 unidades o menos, se muestra el aviso "¡Últimas unidades!".
- **CA-05.3** Desde el detalle se puede elegir una cantidad y agregar el producto al carrito.

### HU-06 · Agregar productos al carrito

**Como** cliente **quiero** agregar productos a mi carrito **para** comprarlos juntos.

**Criterios de aceptación**

- **CA-06.1** Solo los clientes autenticados pueden agregar productos. Si un visitante lo intenta, se le pide iniciar sesión.
- **CA-06.2** La cantidad por producto debe respetar RN-05.
- **CA-06.3** Si el producto ya está en el carrito, se suma la cantidad a la existente, respetando RN-05.
- **CA-06.4** El carrito se conserva entre sesiones del mismo cliente, y entre la web y la app móvil.
- **CA-06.5** El ícono del carrito muestra el número total de unidades.

### HU-07 · Modificar el carrito

**Como** cliente **quiero** cambiar cantidades o quitar productos de mi carrito **para** ajustar mi compra.

**Criterios de aceptación**

- **CA-07.1** Se puede cambiar la cantidad de cada producto, respetando RN-05.
- **CA-07.2** Se puede eliminar un producto del carrito.
- **CA-07.3** Si la cantidad se cambia a 0, el producto se elimina del carrito.
- **CA-07.4** Los totales (sección HU-09) se recalculan con cada cambio.
- **CA-07.5** Si el carrito queda vacío, se muestra "Tu carrito está vacío" y el botón para continuar al checkout se deshabilita.

### HU-08 · Aplicar cupón de descuento

**Como** cliente **quiero** aplicar un cupón **para** obtener un descuento en mi compra.

**Criterios de aceptación**

- **CA-08.1** El carrito tiene un campo para capturar un código de cupón.
- **CA-08.2** Solo se puede aplicar un cupón por orden (RN-07).
- **CA-08.3** Si el cupón es válido, se muestra el descuento aplicado y el nuevo total.
- **CA-08.4** Si el cupón no existe, está vencido o no cumple sus condiciones, se muestra "Cupón no válido" y el total no cambia.
- **CA-08.5** El cliente puede quitar el cupón aplicado.
- **CA-08.6** Las condiciones de cada cupón están en la sección 4.2.

### HU-09 · Cálculo de totales y envío

**Como** cliente **quiero** ver el desglose de mi compra **para** saber cuánto voy a pagar.

**Criterios de aceptación**

- **CA-09.1** El carrito y el checkout muestran: subtotal, descuento, costo de envío y total.
- **CA-09.2** Subtotal = suma de (precio unitario × cantidad) de los productos del carrito.
- **CA-09.3** El costo de envío se calcula según RN-08.
- **CA-09.4** Total = subtotal − descuento + costo de envío.
- **CA-09.5** Todos los importes se redondean a dos decimales.

### HU-10 · Checkout y dirección de envío

**Como** cliente **quiero** confirmar mi compra e indicar a dónde enviarla **para** recibir mis productos.

**Criterios de aceptación**

- **CA-10.1** El checkout pide una dirección de envío con: calle y número, colonia, ciudad, estado, código postal y teléfono de contacto.
- **CA-10.2** El código postal debe tener 5 dígitos y el teléfono 10 dígitos.
- **CA-10.3** El cliente puede guardar la dirección para compras futuras.
- **CA-10.4** Antes de pagar, se muestra un resumen con los productos, el desglose de totales y la dirección.
- **CA-10.5** Al confirmar, se crea una orden en estado "Pendiente de pago" y se pasa al pago.

### HU-11 · Pago simulado

**Como** cliente **quiero** pagar con tarjeta **para** completar mi compra.

**Criterios de aceptación**

- **CA-11.1** El formulario de pago pide: nombre del titular, número de tarjeta, fecha de vencimiento (MM/AA) y CVV.
- **CA-11.2** El número de tarjeta debe tener 16 dígitos y la fecha de vencimiento no puede estar en el pasado. El CVV tiene 3 dígitos.
- **CA-11.3** El resultado del pago depende de la tarjeta usada (sección 4.3).
- **CA-11.4** Si el pago es aprobado, la orden pasa a "Pagada", se descuentan las existencias, se vacía el carrito y se muestra una confirmación con el número de orden.
- **CA-11.5** Si el pago es rechazado, se muestra "Pago rechazado. Verifica tus datos o usa otra tarjeta." y el cliente puede intentarlo de nuevo.
- **CA-11.6** Nunca se guarda el número completo de la tarjeta ni el CVV. En pantallas y comprobantes solo se muestran los últimos 4 dígitos.

### HU-12 · Historial y cancelación de órdenes

**Como** cliente **quiero** consultar mis órdenes y cancelarlas si me arrepiento **para** tener control sobre mis compras.

**Criterios de aceptación**

- **CA-12.1** El cliente ve la lista de sus órdenes, de la más reciente a la más antigua, con número, fecha, total y estado.
- **CA-12.2** Al abrir una orden, se ve su detalle: productos, cantidades, precios, desglose de totales, dirección y estado.
- **CA-12.3** El cliente puede cancelar una orden dentro de las 24 horas, siempre que no haya sido enviada (RN-09).
- **CA-12.4** Al cancelar, la orden pasa a "Cancelada" y las existencias se reintegran al inventario.
- **CA-12.5** Un cliente no puede ver ni modificar órdenes de otros clientes.

---

## 3. Reglas de negocio

| ID | Regla |
|---|---|
| RN-01 | Cada correo electrónico puede registrarse una sola vez. |
| RN-02 | La contraseña debe tener entre 8 y 64 caracteres, con al menos una letra y un número. |
| RN-03 | El cliente debe tener 18 años cumplidos a la fecha de registro. |
| RN-04 | Después de 5 intentos de inicio de sesión fallidos consecutivos, la cuenta se bloquea 15 minutos. |
| RN-05 | La cantidad de un mismo producto en el carrito debe estar entre 1 y 10 unidades, y no puede superar las existencias disponibles. |
| RN-06 | Los precios de los productos incluyen IVA. |
| RN-07 | Solo se puede aplicar un cupón por orden. Los cupones no son acumulables. |
| RN-08 | El costo de envío es de $99.00. El envío es gratis en compras mayores a $999.00. |
| RN-09 | Una orden solo se puede cancelar en estado "Pagada" y dentro de las 24 horas. |
| RN-10 | Estados de una orden: Pendiente de pago → Pagada → Enviada → Entregada. Desde "Pagada" también puede pasar a "Cancelada". |

---

## 4. Datos de referencia

### 4.1 Categorías

Computación · Audio · Telefonía · Hogar · Accesorios

### 4.2 Cupones vigentes

| Código | Descuento | Condiciones |
|---|---|---|
| `BIENVENIDA10` | 10% sobre el subtotal | Solo en la primera compra del cliente |
| `ENVIOGRATIS` | Elimina el costo de envío | Subtotal mínimo de $500.00 |
| `AHORRA200` | $200.00 de descuento | Subtotal mínimo de $1,500.00 |
| `NAVIDAD25` | 25% sobre el subtotal | Vencido (válido hasta el 31/12/2025) |

### 4.3 Tarjetas de prueba del pago simulado

| Número | Resultado |
|---|---|
| 4111 1111 1111 1111 | Pago aprobado |
| 4000 0000 0000 0002 | Rechazado: fondos insuficientes |
| 4000 0000 0000 0069 | Rechazado: tarjeta vencida |
| Cualquier otro número de 16 dígitos | Rechazado: tarjeta no reconocida |

---

## 5. Requisitos no funcionales

| ID | Requisito |
|---|---|
| RNF-01 · Rendimiento | El sistema debe responder rápido. Las páginas del catálogo y del carrito deben cargar en menos de 2 segundos. |
| RNF-02 · Disponibilidad | El sistema debe estar disponible el 99.5% del tiempo mensual. |
| RNF-03 · Seguridad | Las contraseñas se almacenan cifradas con un algoritmo de hash seguro. Toda la comunicación usa HTTPS. |
| RNF-04 · Privacidad | Los mensajes de error y los registros (logs) no deben mostrar datos personales: correo, teléfono, dirección ni datos de tarjeta. |
| RNF-05 · Compatibilidad | La web funciona en las dos últimas versiones de Chrome, Edge, Firefox y Safari, en escritorio y en móvil. La app móvil funciona en Android 10 o superior. |
| RNF-06 · Accesibilidad | Los formularios tienen etiquetas asociadas a cada campo y pueden completarse solo con el teclado. |
