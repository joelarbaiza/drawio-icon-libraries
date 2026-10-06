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
de instalación por defecto (Windows: `C:\Program Files\Inkscape\bin\inkscape.com`, macOS:
`/Applications/Inkscape.app/Contents/MacOS/inkscape`). `--inkscape` e `INKSCAPE` deben apuntar al
**ejecutable**, no a la carpeta. No hace falta WSL.

## Estructura del repositorio

```
libraries.json              Manifiesto: qué carpeta de SVG genera cada librería y cómo se titulan
libraries/<…>.xml           Librerías de Draw.io (GENERADAS: no se editan a mano)
svg/…/<librería>/source/    SVG originales, tal como vienen del proveedor
svg/…/<librería>/64/        SVG normalizados a 64×64 (generados por `normalize`, se commitean)
scripts/build.py            CLI: list · normalize · pack · all
scripts/validate.py         Comprueba las librerías (formato, 64×64, títulos, raster, duplicados)
scripts/compare.py          Compara las librerías icono a icono contra una versión de git
scripts/package.py          Genera el ZIP de la release
scripts/release.py          Calcula la versión siguiente y prepara CHANGELOG.md (lo usa «Publicar versión»)
scripts/iconlib/            Código común (manifiesto, títulos, empaquetado, normalización)
docs/SOURCES.md             Origen y licencia de cada librería e icono
docs/ARCHITECTURE.md        Cómo funciona el pipeline y por qué
.github/workflows/          CI (validate.yml) y versiones (publish.yml → release.yml)
```

> La carpeta exacta de cada librería está en `libraries.json` y la muestra `python scripts/build.py list -v`:
> las de Azure cuelgan de `svg/Azure/`, Fabric está en `svg/Fabric/` y las de Dynamics 365 en carpetas con otro
> nombre (`svg/Dynamics 365/Dynamics 365 App Icons/`). En el resto del documento, `<source>` y `<64>` son esas
> carpetas.

## Comandos frecuentes

```bash
python scripts/build.py list -v                      # librerías, nº de iconos y su carpeta source/
python scripts/build.py all -l "Azure Web"           # normaliza + empaqueta una librería (Inkscape)
python scripts/build.py pack                         # regenera todos los .xml desde svg/*/64 (sin Inkscape)
python scripts/validate.py                           # lo mismo que comprueba la CI
python scripts/build.py pack --check                 # ¿los .xml están al día con sus SVG?
python scripts/compare.py --ref origin/main -v       # qué iconos/títulos cambiaron respecto a main
```

Todos los comandos aceptan `--help`. `normalize`, `pack` y `all` aceptan `--dry-run` para ver qué harían sin
escribir nada. `compare.py` empareja los iconos **por posición**: si añades o quitas iconos, los que van
detrás aparecerán como cambiados; úsalo para comprobar que *no* cambia nada inesperado.

## Añadir iconos a una librería existente

1. Copia los SVG originales a la carpeta `<source>` de la librería (`build.py list -v`). El nombre del
   archivo es el título del icono (después de aplicar las reglas de título; ver más abajo). Si te
   equivocas de carpeta, `pack` falla y te dice qué SVG no pertenece a ninguna librería.
2. Normaliza y empaqueta:
   ```bash
   python scripts/build.py all -l "<librería>"
   ```
   Con la misma versión de Inkscape, los SVG existentes se regeneran idénticos y solo aparecen los nuevos.
   Con otra versión pueden variar decimales del `transform` en todos. Si solo querías añadir iconos,
   restaura los existentes y vuelve a empaquetar:
   ```bash
   git restore "<64>"                                # deshace los SVG modificados (los nuevos siguen)
   python scripts/build.py pack -l "<librería>"
   ```
3. Comprueba y revisa:
   ```bash
   python scripts/validate.py
   ```
   Abre el `.xml` en Draw.io (`Archivo → Abrir biblioteca`) y mira que los iconos se vean bien.
4. Commitea **los tres**: `<source>`, `<64>` y `libraries/<…>.xml`.
5. Anota el origen y la licencia en [docs/SOURCES.md](docs/SOURCES.md) y actualiza el número de iconos
   en la tabla y en la introducción de `README.md` y `README.es.md`.
6. Añade una línea al CHANGELOG (ver [Anotar los cambios en el CHANGELOG](#anotar-los-cambios-en-el-changelog)).

**Solo SVG vectoriales.** Un SVG que embeba imágenes (`<image>` con PNG/JPG) hace fallar `validate.py`:
busca una versión vectorial. Si no existe, justifícalo en `docs/SOURCES.md` y añade el icono a
`RASTER_ALLOWLIST` en `scripts/validate.py`.

Para **quitar o renombrar** un icono, hazlo en `<source>` y ejecuta `build.py all -l "<librería>" --prune`:
`--prune` borra de `<64>` los SVG cuyo original ya no existe (sin él, `pack` falla para avisarte). Si el
icono tenía un título manual, cambia también su clave en `title_overrides`.

## Actualizar una librería con una versión nueva del proveedor

Cuando el proveedor publica una versión nueva de su paquete de iconos (p. ej. Fabric):

1. Descarga el paquete y localiza los SVG (Fabric: `package/dist/svg` dentro de `Icons.zip`).
2. Sustituye **todo** el contenido de `<source>` por los SVG que use la librería, con el mismo criterio de
   selección que la versión anterior (Fabric: los de 48 px, sin `filled` ni `regular`). Así los iconos que el
   proveedor renombra o elimina también desaparecen de la librería.
3. Normaliza, empaqueta y limpia los huérfanos de `<64>`:
   ```bash
   python scripts/build.py all -l "<librería>" --prune
   python scripts/validate.py
   ```
4. Revisa en `git status` qué iconos son nuevos (`??`) y cuáles se eliminan (`D`); compáralo con el
   changelog del proveedor y mira los nuevos en Draw.io.
5. Actualiza la versión y la fecha del paquete en `docs/SOURCES.md`, los contadores de los README y
   el CHANGELOG con los iconos nuevos, renombrados y eliminados (ver
   [Anotar los cambios en el CHANGELOG](#anotar-los-cambios-en-el-changelog)).

Los diagramas que ya usaban un icono eliminado no se rompen: Draw.io guarda una copia del icono dentro
de cada diagrama.

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
4. Añádela a la tabla de `README.md` y `README.es.md` (y actualiza los totales de la introducción), y su
   origen a `docs/SOURCES.md`.
5. Añade una línea al CHANGELOG, en `### Añadido` de `## [Sin publicar]`.
6. Commitea `libraries.json`, las dos carpetas de SVG y el `.xml` nuevo.

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

## Anotar los cambios en el CHANGELOG

Cada PR que cambie iconos, librerías o scripts añade una línea en [CHANGELOG.md](CHANGELOG.md), en la
sección `## [Sin publicar]` (los cambios que ya están en `main` pero aún no tienen versión). Esas líneas
son las notas que aparecerán en la próxima release.

- Solo hay **una** sección `## [Sin publicar]`, siempre arriba del todo: no crees otra.
- Escribe debajo del subtítulo que corresponda; si aún no existe dentro de `Sin publicar`, créalo, en este
  orden: `### Añadido` (iconos o librerías nuevas, funciones nuevas), `### Cambiado` (actualizaciones,
  títulos, rediseños), `### Eliminado`.
- No edites las versiones ya publicadas (`## [1.0.0] - …`).
- Una línea por cambio, pensada para quien usa las librerías: qué librería y qué iconos.

Ejemplo, después de añadir tres iconos a Programming:

```markdown
## [Sin publicar]

### Añadido
- Programming: iconos de `Zig`, `Elixir` y `Haskell`.
```

Al publicar con el botón **Publicar versión** (ver más abajo), ese título se convierte en
`## [1.1.0] - 2026-10-06`, se añade su enlace al final del archivo y arriba queda una sección
`## [Sin publicar]` nueva y vacía para lo siguiente. No hace falta tocar nada más.

## Antes de abrir el Pull Request

La CI ([validate.yml](.github/workflows/validate.yml)) ejecuta esto en Linux con Python 3.9 y 3.x;
pásalo en local para no llevarte sorpresas:

```bash
python scripts/validate.py            # OK
python scripts/build.py pack --check  # OK: N librería(s) al día
python scripts/package.py             # genera dist/drawio-icon-libraries.zip
```

- [ ] SVG originales en `<source>` y normalizados en `<64>`.
- [ ] `.xml` regenerado con `build.py` (nunca editado a mano: `pack --check` lo detecta).
- [ ] Títulos claros y sin duplicados dentro de la librería.
- [ ] Iconos revisados en Draw.io (adjunta una captura al PR si cambian iconos).
- [ ] Origen y licencia en `docs/SOURCES.md`.
- [ ] Línea en `## [Sin publicar]` de `CHANGELOG.md`.

## Ramas y commits

- Ramas desde `main`: `feat/lib-<librería>`, `feat/<tema>`, `fix/<descripción-breve>`.
- Mensajes con el formato de [Conventional Commits](https://www.conventionalcommits.org/es/), en español,
  como el resto del historial: `feat(icons): …`, `fix(scripts): …`, `docs: …`, `ci: …`.

## Publicar una versión (mantenedores)

**Mientras trabajas:** cada PR deja su línea en `## [Sin publicar]` del CHANGELOG
(ver [Anotar los cambios en el CHANGELOG](#anotar-los-cambios-en-el-changelog)).

**Para publicar** (cuando `main` tenga todo lo que quieres sacar):

1. En GitHub: **Actions → Publicar versión → Run workflow**, con la rama `main`.
2. Elige el tipo de versión:
   - `minor` (1.0.0 → 1.1.0): iconos o librerías nuevas, actualizaciones del proveedor.
   - `patch` (1.0.0 → 1.0.1): correcciones (un título, un icono mal normalizado).
   - `major` (1.0.0 → 2.0.0): cambios incompatibles (renombrar o quitar librerías enteras).
3. Listo. [publish.yml](.github/workflows/publish.yml) valida, calcula la versión a partir del último tag,
   convierte `Sin publicar` en `[X.Y.Z] - fecha`, sube la versión en `pyproject.toml`, hace commit en
   `main`, crea el tag y publica la release con el ZIP y las notas del CHANGELOG. El botón de descarga del
   README apunta siempre a la última.

Se niega a publicar si `Sin publicar` está vacía. Después, haz `git pull` en tu copia local: `main` tiene
un commit nuevo (`chore(release): vX.Y.Z`).

Para ver qué haría sin publicar nada: `python scripts/release.py next --bump minor` y
`python scripts/release.py prepare --version X.Y.Z --dry-run`.

Alternativa manual: subir un tag `vX.Y.Z` (`git tag v1.2.0` y `git push origin v1.2.0`) también publica la
release, pero entonces el CHANGELOG y `pyproject.toml` hay que actualizarlos a mano antes.

> Si `main` se protege para exigir PR, el workflow no podrá hacer push de su commit: habrá que permitir
> a GitHub Actions saltarse la protección o volver al flujo manual.

## Problemas frecuentes

| Síntoma | Causa y solución |
|---|---|
| `No se encontró Inkscape` | Instálalo o indica el **ejecutable** (no la carpeta): `--inkscape "C:\Program Files\Inkscape\bin\inkscape.com"` o la variable `INKSCAPE`. |
| `SVG fuera de las carpetas de libraries.json` | Copiaste un SVG a una carpeta que no es la `source/` de ninguna librería. Muévelo a la correcta (`build.py list -v`). |
| `pack --check`: `DESACTUALIZADO` | Cambiaste SVG, títulos o editaste un `.xml` a mano. Ejecuta `python scripts/build.py pack` y commitea el resultado. |
| `SVG normalizados sin original` | Quitaste o renombraste un SVG de `source/`. Ejecuta `python scripts/build.py all -l "<librería>" --prune`. |
| `title_overrides sin SVG correspondiente` | Renombraste o quitaste un icono con título manual. Actualiza su clave en `libraries.json`. |
| `ya está normalizado` | Has puesto en `source/` un SVG de `64/`. Usa el SVG original del proveedor. |
| Avisos `LF will be replaced by CRLF` en Windows | Inofensivos (vienen de `core.autocrlf`). Los SVG y `.xml` se guardan siempre con LF por `.gitattributes`, y `pack` es independiente del SO; en el resto de archivos de texto solo cambia la copia local. |
