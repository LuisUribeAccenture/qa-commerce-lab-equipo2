# Instrucciones para agentes

## Comandos

- API · `pytest tests/api`
- Web · `pytest tests/web`

## Reglas

1. Modifica `app/` solo cuando el encargo lo pida expresamente.
2. Deriva cada resultado esperado de `docs/requisitos.md` y cita el criterio o regla. Señala las partes ambiguas y usa el contrato publicado para las formas y los códigos HTTP que estén especificados.
3. Si una prueba falla porque la aplicación incumple un requisito, detente e informa. Conserva la aserción. Usa `xfail(strict=True)` solo para un defecto documentado que el equipo haya aceptado.
4. Usa datos sintéticos y el dominio `example.com` para correos de prueba.
5. En pruebas de autorización, usa dos identidades independientes y un control positivo. Si se comprueba enumeración en el login, compara el código y el cuerpo de los dos rechazos.
6. En pruebas web con mocks, intercepta las respuestas de la API, valida su forma contra el contrato y comprueba la interfaz con las esperas automáticas de Playwright.

## Al terminar

Informa los comandos ejecutados y su resultado real.
