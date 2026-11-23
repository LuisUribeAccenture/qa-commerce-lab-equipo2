# Entrega del módulo 3

## 1. Un fixture generado por IA

**Resultado en Chromium:** `pytest tests/web/test_fixture_propio.py` → `1 passed`. La app se ejecutó en `http://127.0.0.1:8000` con una base de datos de prueba.

1. **¿El fixture crea su propio producto o usa uno de los datos base?** Crea un producto activo en la categoría `Hogar`, con precio de 120.00, 3 unidades y un nombre único generado con `uuid4()`.
2. **¿Usa `/api/test/seed` y la función `_post`?** Sí. `_post` envía el JSON al mismo servidor que usa Playwright. El endpoint devuelve una lista de IDs en `products`, así que el fixture devuelve `resultado["products"][0]`.
3. **¿Qué pasaría si otra prueba compra antes ese producto? ¿Por qué no pasa aquí?** Si compra una o dos unidades, el aviso sigue visible porque quedan entre 1 y 5. Si compra las tres, el aviso desaparece y la prueba falla. El fixture se ejecuta para cada prueba que lo pide, crea el producto durante su preparación y le entrega el ID recién generado. Por eso las compras que hayan hecho pruebas anteriores no afectan ese registro.

