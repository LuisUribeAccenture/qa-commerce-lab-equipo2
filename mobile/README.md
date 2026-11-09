# Cliente móvil de QA Commerce Lab (Android)

App Android mínima que usa la misma API REST que la web: inicio de sesión, catálogo con búsqueda, agregar al carrito y carrito con cantidades y totales.

## Usarla (no hace falta compilar)

1. Levanta la API en tu equipo: `uvicorn app.main:app` (puerto 8000).
2. Arranca un emulador Android (Android 10 o superior).
3. Instala el APK incluido en esta carpeta:

   ```bash
   adb install -r mobile/qa-commerce-lab.apk
   ```

4. Abre **QA Commerce Lab** en el emulador. El campo **Servidor** ya trae `http://10.0.2.2:8000`, la dirección con la que el emulador ve el `localhost` de tu equipo. Entra con `ana.garcia@example.com` / `Password123`.

> En un teléfono físico, usa la IP de tu equipo en la red local (por ejemplo, `http://192.168.1.20:8000`) y levanta la API con `uvicorn app.main:app --host 0.0.0.0`.

## Datos para automatizar con Appium

| Dato | Valor |
|---|---|
| `appPackage` | `mx.tec.qacl` |
| `appActivity` | `.LoginActivity` |
| Driver | UiAutomator2 |

Los elementos tienen `resource-id` (por ejemplo, `mx.tec.qacl:id/login_email`) y descripción accesible (por ejemplo, `Correo electrónico`, `Agregar Teclado Mecánico Kappa al carrito`, `Total`). Prefiere la descripción accesible.

| Pantalla | Elementos principales (descripción accesible) |
|---|---|
| Inicio de sesión | `Servidor`, `Correo electrónico`, `Contraseña`, `Entrar` · error en `login_error` |
| Catálogo | `Buscar producto`, `Buscar`, `Carrito`, `Salir`, `Agregar <producto> al carrito` · resultados en `catalog_info` |
| Carrito | `Aumentar <producto>`, `Disminuir <producto>`, `Subtotal`, `Descuento`, `Envío`, `Total`, `Seguir comprando` |

## Compilar desde el código (opcional)

Requiere JDK 17 y el SDK de Android.

```bash
cd mobile/android
./gradlew assembleDebug      # Windows: gradlew.bat assembleDebug
```

El APK queda en `app/build/outputs/apk/debug/app-debug.apk`.
