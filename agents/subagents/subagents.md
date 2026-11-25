Meta: propón un plan de pruebas negativas para la API de QA Commerce Lab.
Fuentes: docs/requisitos.md, tests/api/conftest.py y app/schemas.py.
Cubre:- Autorización (OWASP API1): api_ana y api_luis; la orden 1 es de Luis.- Autenticación (OWASP API2): tokens y respuestas del login.- Mensajes de error sin datos personales (RNF-04).- Entradas inválidas: tipos, campos faltantes y valores fuera de rango.
Entrega una tabla: caso, petición, resultado esperado, requisito y control.
Límites: no escribas archivos y no consultes la respuesta actual de la API
para decidir el resultado esperado. Si el requisito no lo dice, escribe «ambiguo».
Verificación: cada resultado esperado cita el requisito de donde sale.
Alto: entrega la tabla y espera.