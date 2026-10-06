# Cómo contribuir

¡Gracias por ayudar! Esta guía explica cómo añadir iconos o librerías, cómo regenerar los `.xml`
y qué se comprueba antes de aceptar un Pull Request. Si quieres entender *por qué* funciona así,
lee [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Requisitos

| Para… | Necesitas |
|---|---|
| Cambiar títulos, regenerar los `.xml`, validar | **Python 3.9+** (solo biblioteca estándar) y Git |
| Añadir o cambiar iconos (normalizar SVG a 64×64) | Lo anterior + **[Inkscape 1.x](https://inkscape.org)** + **Pillow** (`pip install -r requirements.txt`) |

`build.py` busca Inkscape en este orden: `--inkscape RUTA`, la variable `INKSCAPE`, el `PATH` y la ruta
de instalación por defecto (Windows: `C:\Program Files\Inkscape\bin`, macOS: `/Applications/Inkscape.app`).
No hace falta WSL.

## Estructura del repositorio

```
libraries.json              Manifiesto: qué carpeta de SVG genera cada librería y cómo se titulan
libraries/<…>.xml           Librerías de Draw.io (GENERADAS: no se editan a mano)
svg/<librería>/source/      SVG originales, tal como vienen del proveedor
svg/<librería>/64/          SVG normalizados a 64×64 (generados por `normalize`, se commitean)
scripts/build.py            CLI: list · normalize · pack · all
scripts/validate.py         Comprueba las librerías (formato, 64×64, títulos, raster, duplicados)
scripts/compare.py          Compara las librerías icono a icono contra una versión de git
scripts/package.py          Genera el ZIP de la release
scripts/iconlib/            Código común (manifiesto, títulos, empaquetado, normalización)
docs/SOURCES.md             Origen y licencia de cada librería e icono
docs/ARCHITECTURE.md        Cómo funciona el pipeline y por qué
.github/workflows/          CI (validate.yml) y publicación de versiones (release.yml)
```

## Comandos frecuentes

```bash
python scripts/build.py list                         # librerías del manifiesto y nº de iconos
python scripts/build.py all -l "Azure Web"           # normaliza + empaqueta una librería (Inkscape)
python scripts/build.py pack                         # regenera todos los .xml desde svg/*/64 (sin Inkscape)
python scripts/validate.py                           # lo mismo que comprueba la CI
python scripts/build.py pack --check                 # ¿los .xml están al día con sus SVG?
python scripts/compare.py --ref main -v              # qué iconos/títulos cambiaron respecto a main
```

Todos los comandos aceptan `--help`, y `build.py` acepta `--dry-run` para ver qué haría sin escribir nada.

## Añadir iconos a una librería existente

1. Copia los SVG originales a `svg/<librería>/source/`. El nombre del archivo es el título del icono
   (después de aplicar las reglas de título de la librería; ver más abajo).
2. Normaliza y empaqueta:
   ```bash
   python scripts/build.py all -l "<librería>"
   ```
   Con la misma versión de Inkscape, los SVG existentes se regeneran idénticos y solo aparecen los nuevos.
   Con otra versión pueden variar decimales del `transform` en todos: si solo añades iconos, puedes
   descartar esos cambios con `git checkout -- "svg/<librería>/64"` antes de añadir los nuevos.
3. Comprueba y revisa:
   ```bash
   python scripts/validate.py
   ```
   Abre el `.xml` en Draw.io (`Archivo → Abrir biblioteca`) y mira que los iconos se vean bien.
4. Commitea **los tres**: `svg/<librería>/source/`, `svg/<librería>/64/` y `libraries/<…>.xml`.
5. Anota el origen y la licencia en [docs/SOURCES.md](docs/SOURCES.md).

**Solo SVG vectoriales.** Un SVG que embeba imágenes (`<image>` con PNG/JPG) hace fallar `validate.py`:
busca una versión vectorial. Si no existe, justifícalo en `docs/SOURCES.md` y añade el icono a
`RASTER_ALLOWLIST` en `scripts/validate.py`.

Para **quitar o renombrar** un icono, hazlo en `source/` y ejecuta `build.py all -l "<librería>" --prune`:
`--prune` borra de `64/` los SVG cuyo original ya no existe (sin él, `pack` falla para avisarte).

## Añadir una librería nueva

1. Crea `svg/<categoría>/<librería>/source/` (o `svg/<librería>/source/`) con los SVG originales.
2. Añade una entrada en [libraries.json](libraries.json):
   ```json
   {
     "name": "Mi Librería",
     "source": "svg/Mi Librería/source",
     "normalized": "svg/Mi Librería/64",
     "output": "libraries/Mi Librería/Mi Librería.xml",
     "title_rules": []
   }
   ```
3. `python scripts/build.py all -l "Mi Librería"` y `python scripts/validate.py`.
4. Añádela a la lista de librerías de `README.md` y `README.es.md`, y su origen a `docs/SOURCES.md`.

## Títulos de los iconos

El título visible en Draw.io sale del nombre del archivo (sin `.svg`, con `_` → espacio) y luego se
limpia con las reglas de `title_rules`, en orden. Reglas disponibles (`python scripts/build.py list`):

| Regla | Ejemplo |
|---|---|
| `strip_azure_prefix` | `00028-icon-service-Batch-AI` → `Batch-AI` |
| `dash_to_space` | `Batch-AI` → `Batch AI` |
| `strip_scalable` | `BusinessCentral scalable (1)` → `BusinessCentral` |
| `split_camel_case` | `BusinessCentral` → `Business Central`, `AIBuilder` → `AI Builder` |
| `fabric_suffix` | `lakehouse 48 item` → `lakehouse`, `data warehouse 48 color` → `data warehouse (color)` |
| `strip_color_icon` | `Microsoft Entra ID color icon` → `Microsoft Entra ID` |

Para un caso que ninguna regla resuelve, fija el título a mano con `title_overrides`
(clave: nombre del archivo sin `.svg`):

```json
"title_overrides": { "00330-icon-service-Workspaces": "Workspaces (Virtual Desktop)" }
```

Cambiar títulos **no requiere Inkscape**: edita `libraries.json` y ejecuta `python scripts/build.py pack`.
Una regla nueva se añade en `scripts/iconlib/titles.py`; si deja algún patrón «crudo» nuevo, añádelo
también a `RAW_TITLE_PATTERNS` en `scripts/validate.py`.

## Antes de abrir el Pull Request

La CI ([validate.yml](.github/workflows/validate.yml)) ejecuta esto en Linux con Python 3.9 y 3.x;
pásalo en local para no llevarte sorpresas:

```bash
python scripts/validate.py          # OK
python scripts/build.py pack --check  # OK: 30 librería(s) al día
```

- [ ] SVG originales en `svg/<librería>/source/` y normalizados en `svg/<librería>/64/`.
- [ ] `.xml` regenerado con `build.py` (nunca editado a mano: `pack --check` lo detecta).
- [ ] Títulos claros y sin duplicados dentro de la librería.
- [ ] Iconos revisados en Draw.io (adjunta una captura al PR si cambian iconos).
- [ ] Origen y licencia en `docs/SOURCES.md`.

## Ramas y commits

- Ramas desde `main`: `feat/lib-<librería>`, `feat/<tema>`, `fix/<descripción-breve>`.
- Mensajes con el formato de [Conventional Commits](https://www.conventionalcommits.org/es/), en español,
  como el resto del historial: `feat(icons): …`, `fix(scripts): …`, `docs: …`, `ci: …`.

## Publicar una versión (mantenedores)

1. Actualiza [CHANGELOG.md](CHANGELOG.md) y haz merge a `main`.
2. Crea y sube el tag desde `main`:
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```
3. [release.yml](.github/workflows/release.yml) valida, genera `drawio-icon-libraries.zip` y publica la
   release. El botón de descarga del README apunta siempre a la última.

## Problemas frecuentes

| Síntoma | Causa y solución |
|---|---|
| `No se encontró Inkscape` | Instálalo o indica la ruta: `--inkscape "C:\Program Files\Inkscape\bin\inkscape.com"` o la variable `INKSCAPE`. |
| `pack --check`: `DESACTUALIZADO` | Cambiaste SVG, títulos o editaste un `.xml` a mano. Ejecuta `python scripts/build.py pack` y commitea el resultado. |
| `SVG normalizados sin original` | Quitaste o renombraste un SVG de `source/`. Ejecuta `normalize --prune`. |
| `ya está normalizado` | Has puesto en `source/` un SVG de `64/`. Usa el SVG original del proveedor. |
| Avisos `LF will be replaced by CRLF` en Windows | Inofensivos: `.gitattributes` guarda los SVG y `.xml` con LF y `pack` es independiente del SO. |
