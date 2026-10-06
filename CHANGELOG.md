# Changelog

Cambios relevantes del proyecto. Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/);
las versiones siguen [Versionado Semántico](https://semver.org/lang/es/).

## [Sin publicar]

### Añadido
- `CLAUDE.md`: guía para trabajar en el repo con Claude Code (comandos, reglas, trampas conocidas y tareas
  habituales).

### Cambiado
- README: la insignia de versión pasa a llamarse «latest version» / «última versión» y se explica qué hace
  cada botón de la sección de descarga (descargar el ZIP o ver las notas de la versión).

## [1.1.1] - 2026-10-06

### Cambiado
- CI: acciones de GitHub actualizadas a `actions/checkout@v7` y `actions/setup-python@v7`, que usan
  Node 24 (GitHub retira Node 20 de los runners).
- **Python mínimo: 3.14** (antes 3.9, sin soporte desde octubre de 2025 y sin versión para Ubuntu 26.04,
  al que pasa `ubuntu-latest` el 19-10-2026). La CI prueba 3.14 y la versión estable más reciente.

## [1.1.0] - 2026-10-06

### Añadido
- Botón **Publicar versión** en GitHub Actions (`publish.yml` + `scripts/release.py`): calcula la versión,
  actualiza el CHANGELOG y `pyproject.toml`, crea el tag y publica la release sin pasos manuales.
- Las notas de cada release salen de su sección del CHANGELOG.

### Cambiado
- **Microsoft Fabric** actualizada al paquete oficial `@fabric-msft/svg-icons` v6.1.0 (licencia MIT): 71 → 77 iconos.
  - Nuevos: `custom streaming connector`, `data agent`, `data factory`, `graph intelligence (color)`,
    `graph model instance`, `graph model instance queryset`, `mobile report`, `operations agent`, `planning`,
    `purview (color)`, `rdl report`, `runtime lineage`, `user data function`, `variable library`.
  - Renombrados por Microsoft: `ai skills` → `data agent`, `function` → `user data function`,
    `variables` → `variable library`.
  - Eliminados (ya no están en el paquete): `reflex` (ahora Activator, sin icono de 48 px en v6.1.0),
    `digital twin builder`, `digital twin builder flow`, `event schema set`, `metric sets (items)`.
  - Los otros 63 iconos se regeneran con el SVG nuevo; su aspecto no cambia.

## [1.0.0] - 2026-10-05

Primera versión con pipeline reproducible, CI y releases.

### Añadido
- `scripts/build.py`: CLI para normalizar SVG a 64×64 (`normalize`, con Inkscape) y generar las librerías
  (`pack`, solo Python). Sustituye a los 31 notebooks con rutas fijas.
- `libraries.json`: manifiesto con las 30 librerías, sus carpetas, reglas de título y títulos manuales.
- `scripts/validate.py`, `scripts/compare.py` y `scripts/package.py`.
- `pack` falla si hay SVG fuera de las carpetas de `libraries.json` o huérfanos entre `source/` y `64/`,
  para que un icono copiado a la carpeta equivocada no se pierda en silencio.
- CI en GitHub Actions (`validate.yml`) y publicación automática de releases con ZIP (`release.yml`).
- Documentación: `CONTRIBUTING.md`, `docs/ARCHITECTURE.md`, `docs/SOURCES.md`.

### Cambiado
- **Títulos legibles y buscables** en 635 iconos: `00028-icon-service-Batch-AI` → `Batch AI`,
  `BusinessCentral scalable` → `Business Central`, `lakehouse 48 item` → `lakehouse`,
  `Microsoft Entra ID color icon` → `Microsoft Entra ID`.
- **27 iconos raster sustituidos por versiones vectoriales** del mismo diseño (25 de Office 365, Windows y
  Micronaut). Power Apps, Power Automate y Power BI de Office 365 pasan al diseño 2025.
  `Office 365.xml` baja de 5,0 MB a 262 KB.
- Estructura de `svg/` uniforme: cada librería tiene `source/` (originales) y `64/` (normalizados).
- Los SVG se embeben con saltos de línea LF: las librerías son idénticas byte a byte al generarlas en
  Windows, macOS o Linux.
- El botón de descarga del README apunta a la última release en lugar de a un servicio de terceros.

### Eliminado
- 31 notebooks de Jupyter (disponibles en el tag `v0-legacy`).
- 3.010 PNG y SVG de Fabric sin uso (33 MB), también del historial de git.

[1.1.1]: https://github.com/joelarbaiza/drawio-icon-libraries/releases/tag/v1.1.1
[1.1.0]: https://github.com/joelarbaiza/drawio-icon-libraries/releases/tag/v1.1.0
[1.0.0]: https://github.com/joelarbaiza/drawio-icon-libraries/releases/tag/v1.0.0
