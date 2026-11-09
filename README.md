# QA Commerce Lab

Tienda en línea ficticia para practicar **Testing & QA asistido por IA**. Incluye una API REST documentada con OpenAPI, una aplicación web y datos de ejemplo que se reinician con un solo comando.

> Sistema creado exclusivamente para capacitación. Todos los datos son ficticios.

## Requisitos

- Python 3.10 o superior
- Git
- Opcional: Docker

## Puesta en marcha

```bash
git clone <url-del-repositorio>
cd qa-commerce-lab
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements-dev.txt
python -m playwright install chromium
uvicorn app.main:app --reload
```

Abre <http://localhost:8000>.

### Verificar el entorno

```bash
python tools/check_env.py
```

Revisa herramientas, dependencias, navegador de Playwright, acceso a la red y que la app arranque. Al final imprime una línea de resumen para entregar en Cypher.

### En GitHub Codespaces

El repositorio incluye `.devcontainer/`. Al abrirlo en Codespaces se instala todo automáticamente; la app queda disponible en el puerto 8000.

### Con Docker

```bash
docker build -t qa-commerce-lab .
docker run --rm -p 8000:8000 qa-commerce-lab
```

## Qué hay disponible

| URL | Descripción |
|---|---|
| <http://localhost:8000> | Aplicación web |
| <http://localhost:8000/docs> | Documentación interactiva de la API (Swagger UI) |
| <http://localhost:8000/openapi.json> | Contrato OpenAPI |

### Usuarios de ejemplo

| Nombre | Correo | Contraseña |
|---|---|---|
| Ana García | `ana.garcia@example.com` | `Password123` |
| Luis Pérez | `luis.perez@example.com` | `Password123` |

Las tarjetas de prueba y los cupones están en [docs/requisitos.md](docs/requisitos.md), secciones 4.2 y 4.3.

### Endpoints de apoyo para pruebas

Solo existen en el entorno de laboratorio. Se desactivan con `QACL_TEST_ENDPOINTS=0`.

| Endpoint | Uso |
|---|---|
| `POST /api/test/reset` | Borra todo y vuelve a cargar los datos base |
| `POST /api/test/seed` | Agrega usuarios, productos o cupones (ver `/docs`) |
| `POST /api/test/orders/{id}/status` | Cambia el estado de una orden (por ejemplo, a "Enviada") |

## Pruebas

```bash
pytest
```

## Estructura

```
app/
  main.py          # arranque de la app y rutas web
  routes/          # endpoints de la API (auth, products, cart, orders, testing)
  pricing.py       # cálculo de totales, envío y cupones
  seed.py          # datos base deterministas
  templates/       # páginas HTML
  static/          # JavaScript y estilos del cliente web
docs/
  requisitos.md    # documento de requisitos del sistema
tests/
  smoke/           # pruebas smoke
mobile/            # cliente Android (APK incluido) y su código fuente
integradora/       # plantillas de la actividad integradora
```

Durante el curso se agregarán carpetas como `prompts/`, `data/`, `tests/web/`, `tests/api/`, `tests/mobile/` y `perf/`.

## Configuración

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `QACL_DB` | `qa_commerce.db` | Ruta del archivo SQLite |
| `QACL_TEST_ENDPOINTS` | `1` | `0` desactiva los endpoints `/api/test` |
