# Kit de QA asistido por IA — Equipo <nombre>

**Área:** <A · Cuentas y sesión | B · Catálogo y búsqueda | C · Carrito y cupones | D · Checkout y pago | E · Órdenes>

## Integrantes

| Nombre | Rol principal en el equipo |
|---|---|
|  |  |
|  |  |
|  |  |
|  |  |

## Cómo ejecutar el kit

```bash
# Levantar la app
uvicorn app.main:app

# Pruebas de API
pytest tests/api

# Pruebas web
<comando>

# Prueba móvil
<comando>

# Rendimiento
k6 run perf/<script>.js
```

## Contenido

- [Estrategia y matriz de pruebas](estrategia.md)
- [Reporte de defectos](defectos.md)
- [Bitácora de uso de IA](bitacora_ia.md)
- [Política de uso de IA](politica_ia.md)
- Prompts: `prompts/` · Datos: `data/` · Skill: `.agents/skills/<nombre>/`

## Adaptaciones acordadas con el instructor

<Si algún componente se hizo con una alternativa, indícalo aquí.>
