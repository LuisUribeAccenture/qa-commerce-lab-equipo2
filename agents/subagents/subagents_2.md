Meta: implementa en tests/api/test_seguridad_api.py solo los casos aprobados.
Fuentes: la tabla de abajo, docs/requisitos.md y tests/api/conftest.py.
Límites: edita solo ese archivo. Conserva la prueba de ejemplo. No toques app/.
Cada prueba comprueba código y mensaje, y cita su requisito en un comentario.
Verificación: ejecuta pytest tests/api/test_seguridad_api.py -v y muestra el resultado.
Alto: si una prueba falla porque la app no cumple el requisito, no cambies la
aserción ni agregues xfail: detente, informa el fallo y espera al equipo.
Casos aprobados:

Tabla sin formato 16x5 columnas:
Caso
Petición
Resultado esperado
Requisito
Control
API1 · Listado de órdenes
Listar órdenes con api_ana.
La orden 1 queda fuera del listado.
CA-12.1, CA-12.5
El listado de api_luis incluye la orden 1.
API1 · Detalle ajeno
Consultar la orden 1 con api_ana.
Se deniega el acceso y se omiten los datos de la orden.
CA-12.2, CA-12.5, RNF-04
api_luis puede consultar esa misma orden.
API1 · Cancelación ajena
Intentar con api_ana cancelar una orden de Luis pagada hace menos de 24 horas y aún sin enviar.
Se deniega la cancelación. El estado y el inventario quedan intactos.
CA-12.3–CA-12.5
Desde el mismo estado inicial, api_luis puede cancelarla y se reintegran las unidades.
API2 · Token ausente o inválido
Intentar agregar una unidad disponible al carrito, primero sin token y luego con un token sintético inválido.
Se requiere autenticación y el carrito queda intacto.
CA-06.1
Repetir con una sesión válida y comprobar el alta.
API2 · Sesión expirada
Intentar agregar al carrito tras más de 30 minutos de inactividad.
Se requiere iniciar sesión de nuevo. El alta no se realiza.
CA-02.5, CA-06.1
Repetir con una sesión equivalente con menos de 30 minutos de inactividad.
API2 · Respuesta del login
Enviar a POST /api/auth/login un correo inexistente y, en otra petición, un correo registrado con contraseña incorrecta.
Ambas respuestas muestran «Correo o contraseña incorrectos» y dejan al cliente sin sesión autenticada.
CA-02.1, CA-02.2
Iniciar sesión con credenciales correctas de la cuenta registrada.
API2 · Bloqueo
En cuentas aisladas, hacer 4 o 5 intentos fallidos consecutivos y luego enviar credenciales correctas.
Tras 4 fallos puede iniciar sesión. Tras 5, durante los 15 minutos de bloqueo aparece «Cuenta bloqueada temporalmente. Intenta más tarde.».
CA-02.1, CA-02.3, CA-02.4, RN-04
Comprobar que las credenciales correctas vuelven a funcionar después de los 15 minutos.
Privacidad · Errores y logs
Provocar errores de registro, dirección y pago con valores sintéticos identificables.
Los mensajes y logs omiten el correo, teléfono, dirección y datos de tarjeta enviados.
RNF-04
Confirmar que cada petición alcanzó la validación esperada y revisar los registros correspondientes.
Entrada · Tipos incompatibles
Agregar al carrito con quantity como objeto JSON y, por separado, confirmar el checkout con address como lista.
Se rechazan ambos cuerpos.
CartItemIn.quantity, OrderIn.address
Repetir con un entero y un objeto de dirección válido.
Entrada · Campo obligatorio omitido
Enviar a POST /api/auth/register cinco variantes que omitan, de una en una, los campos obligatorios.
Cada registro se rechaza y se identifica el campo inválido.
CA-01.1, CA-01.2, CA-01.7
Registrar una cuenta sintética con los cinco campos válidos.
Entrada · Datos de registro inválidos
Enviar, por separado, correo mal formado, contraseña de 7 o 65 caracteres o fecha de nacimiento de un menor.
Cada registro se rechaza y se identifica el campo inválido.
CA-01.3–CA-01.5, CA-01.7, RN-02, RN-03
Probar correo válido, contraseñas de 8 y 64 caracteres con letra y número, y una fecha de 18 años cumplidos.
Entrada · Cantidad fuera de rango
Agregar al carrito vacío 0 u 11 unidades con stock 20, o 6 unidades con stock 5.
Se rechaza el alta y el carrito sigue vacío.
CA-06.2, RN-05
Probar 1 y 10 unidades con stock 20, y 5 unidades con stock 5.
Entrada · Dirección inválida
Confirmar checkout con CP de 4 o 6 dígitos, o teléfono de 9 u 11, variando un campo por petición.
Se rechaza la dirección y el checkout queda sin confirmar.
CA-10.2, CA-10.5
Repetir con CP de 5 dígitos y teléfono de 10.
Entrada · Pago inválido
Enviar tarjeta de 15 o 17 dígitos, vencimiento del mes anterior o CVV de 2 o 4 dígitos, variando un campo por petición.
Se rechaza el pago y la orden queda sin pagar.
CA-11.2, CA-11.4
Con el reloj fijo, usar una tarjeta de prueba aprobada, vencimiento en el mes actual y CVV de 3 dígitos