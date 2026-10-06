# CLAUDE.md

Guía para Claude Code (y para quien trabaje con él) en este repositorio. Detalle completo en
[CONTRIBUTING.md](CONTRIBUTING.md) (cómo hacer cada tarea) y [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
(por qué funciona así). Si algo de aquí contradice al código, manda el código: avísalo y corrige este archivo.

## Qué es

Librerías de iconos para Draw.io / diagrams.net (formato `mxlibrary`, `.xml`): 30 librerías de iconos
vectoriales normalizados a 64×64 (Azure, Fabric, Office 365, Dynamics 365, Power Platform, Entra ID,
Programming…). El repo contiene los SVG, el pipeline en Python que genera los `.xml` y la CI que los
valida y publica.

Idioma del proyecto: **español** (código, mensajes del CLI, docs, commits). `README.md` es la excepción:
está en inglés y `README.es.md` es su traducción; cualquier cambio en uno va también en el otro.

## Flujo de datos

```
svg/…/<lib>/source/*.svg ──normalize──▶ svg/…/<lib>/64/*.svg ──pack──▶ libraries/…/<lib>.xml
   (SVG del proveedor)     Inkscape+Pillow   (se commitean)       stdlib     (se commitean)
```

`libraries.json` es la única fuente de verdad: por librería, su carpeta `source`, su carpeta `normalized`
(`64/`), el `.xml` de salida, `title_rules` y `title_overrides`.

## Comandos

Ejecuta todo desde la raíz del repo. Requiere **Python 3.14+**. Todos aceptan `--help`.

```bash
python scripts/build.py list -v                  # librerías, nº de iconos y carpeta source/ de cada una
python scripts/build.py pack                     # regenera todos los .xml desde 64/ (rápido, sin Inkscape)
python scripts/build.py pack --check             # ¿los .xml coinciden con sus SVG? (lo que mira la CI)
python scripts/build.py all -l "<librería>"      # normalize + pack de una librería (Inkscape, 1–4 s/icono)
python scripts/build.py all -l "<librería>" --prune   # además borra de 64/ los SVG sin original
python scripts/validate.py [-v]                  # formato, 64×64, títulos, raster, duplicados
python scripts/compare.py --ref origin/main -v   # diferencias icono a icono contra otra versión
python scripts/package.py                        # ZIP de la release en dist/ (ignorado por git)
python scripts/readme.py [--check]               # regenera tabla, enlaces a diagrams.net y totales de los README
python scripts/release.py next --bump minor      # versión que calcularía el botón «Publicar versión»
```

`normalize`, `pack` y `all` aceptan `--dry-run`. `normalize` solo hace falta si cambian SVG de `source/`;
para títulos o el manifiesto basta `pack`.

**Verificación antes de dar una tarea por terminada** (es lo que ejecuta la CI):

```bash
python scripts/validate.py && python scripts/build.py pack --check && python scripts/readme.py --check
```

## Reglas (no las rompas)

1. **Nunca edites `libraries/**/*.xml` a mano.** Son salida generada: cambia los SVG o `libraries.json` y
   ejecuta `build.py`. `pack --check` detecta cualquier edición manual.
2. **Los SVG nuevos van a la carpeta `source` que declara `libraries.json`**, no a una ruta inventada.
   Las rutas no siguen un patrón único (`svg/Azure/<lib>/source`, `svg/Fabric/source`,
   `svg/Dynamics 365/Dynamics 365 App Icons/source`…): consúltalas con `build.py list -v`.
   `pack` falla si hay SVG fuera de esas carpetas.
3. **Commitea juntos `source/`, `64/` y el `.xml`** de la librería que cambies (y `libraries.json` si cambia).
4. **Solo SVG vectoriales.** Un `<image>` (PNG/JPG embebido) hace fallar `validate.py`. `RASTER_ALLOWLIST`
   está vacía a propósito: no añadas excepciones sin justificarlas en `docs/SOURCES.md` y sin preguntar.
5. **No metas en `source/` un SVG ya normalizado** (tiene `<g data-normalized="1">`): `normalize` lo rechaza.
6. **Cada cambio visible anota una línea en `## [Sin publicar]` de `CHANGELOG.md`**, en el mismo commit o PR,
   bajo `### Añadido`, `### Cambiado` o `### Eliminado` (en ese orden; crea el subtítulo si no existe).
   Solo hay una sección `Sin publicar`; no edites versiones ya publicadas.
7. **Origen y licencia de cada icono nuevo en `docs/SOURCES.md`.** Si el origen no tiene licencia clara,
   pregunta antes de usarlo. Los iconos son marcas de terceros: no los modifiques más allá de normalizarlos.
8. **Al añadir o quitar iconos o librerías, ejecuta `python scripts/readme.py`.** Genera en los dos README
   la tabla de librerías (iconos y enlace «Open ↗» a diagrams.net) y los totales de la introducción. Nunca
   edites a mano lo que hay entre `<!-- BEGIN GENERATED: libraries -->` / `<!-- totals -->` y sus cierres.
9. **No versiones a mano.** No edites la versión de `pyproject.toml`, no conviertas `Sin publicar` en una
   versión y no crees tags: lo hace el workflow «Publicar versión» desde `main`.
10. **No hagas `git push`, no crees PR ni lances workflows sin que el usuario lo pida.**

## Títulos de los iconos

Título = nombre del archivo sin `.svg`, `_` → espacio, y luego `title_rules` de la librería en orden
(`scripts/iconlib/titles.py`): `strip_azure_prefix`, `dash_to_space`, `strip_scalable`, `split_camel_case`,
`fabric_suffix`, `strip_color_icon`. Para un caso puntual usa `title_overrides` en `libraries.json`
(clave: nombre del archivo sin `.svg`). Una regla nueva que elimine un patrón «crudo» va acompañada de su
patrón en `RAW_TITLE_PATTERNS` de `scripts/validate.py`. Los títulos deben ser únicos dentro de cada librería.

## Trampas conocidas

- **Saltos de línea.** `.gitattributes` fuerza LF en `*.svg` y `libraries/**/*.xml`; `pack` convierte CRLF→LF
  y `normalize` escribe en binario. Gracias a eso los `.xml` son idénticos en Windows, macOS y Linux.
  No quites ninguna de las tres piezas. Los avisos `LF will be replaced by CRLF` de git en Windows son inofensivos.
- **Inkscape** se busca en `--inkscape`, `$INKSCAPE`, el `PATH` y la ruta de instalación habitual
  (Windows: `C:\Program Files\Inkscape\bin\inkscape.com`). `--inkscape`/`INKSCAPE` deben apuntar al
  ejecutable, no a la carpeta. Con otra versión de Inkscape, `normalize` puede variar decimales del
  `transform` de todos los iconos: si solo querías añadir iconos, `git restore` los `64/` modificados y `pack`.
- **`compare.py` empareja por posición**: si cambia el número de iconos, los posteriores salen como
  cambiados. Sirve para comprobar que *no* cambia nada inesperado.
- **Enlaces a diagrams.net** (`readme.py`): parámetro `clibs` con la URL raw de cada `.xml` en `main`,
  codificada **una sola vez**. Con doble codificación cargan igual, pero diagrams.net muestra el título
  como `Microsoft%20Fabric`. Solo funcionan en la versión web; la app de escritorio usa el ZIP.
- **`scripts/iconlib/`** se llama así porque `.gitignore` (plantilla de Python) ignora `lib/`.
- **`TODO.md`** es un archivo local del mantenedor, ignorado por git: no lo uses como documentación.
- **Dependencias**: solo biblioteca estándar, salvo Pillow (importado de forma diferida, solo en
  `normalize`). No añadas dependencias sin preguntar.
- **Consola de Windows**: los scripts reconfiguran stdout a UTF-8; si escribes uno nuevo, haz lo mismo.

## Tareas habituales (resumen)

| Tarea | Pasos |
|---|---|
| Añadir iconos a una librería | SVG a su `source/` → `build.py all -l "<lib>"` → `validate.py` → `readme.py`, `SOURCES.md`, CHANGELOG |
| Quitar/renombrar iconos | cambia `source/` → `build.py all -l "<lib>" --prune` → actualiza `title_overrides` si aplica → CHANGELOG |
| Actualizar una librería con una versión nueva del proveedor | sustituye **todo** `source/` con el mismo criterio de selección → `all --prune` → revisa `git status` contra el changelog del proveedor → `SOURCES.md` (versión y fecha), `readme.py`, CHANGELOG |
| Librería nueva | carpeta `source/` + entrada en `libraries.json` → `all -l` → `readme.py`, `SOURCES.md`, CHANGELOG |
| Cambiar un título | `title_rules`/`title_overrides` en `libraries.json` → `build.py pack` → CHANGELOG |
| Cambiar un script | mantén Python 3.14+ y solo stdlib → `validate.py`, `pack --check` y prueba el comando tocado |

Paso a paso completo de cada una en [CONTRIBUTING.md](CONTRIBUTING.md).

## CI y versiones

- `validate.yml`: en cada PR y push a `main`, Ubuntu, Python 3.14 y 3.x → `validate.py`, `pack --check`, `package.py`, `readme.py --check`.
- `publish.yml` («Publicar versión», manual desde `main`, patch/minor/major): calcula la versión con
  `scripts/release.py`, convierte `Sin publicar` en `[X.Y.Z] - fecha`, sube la versión en `pyproject.toml`,
  hace commit, tag y llama a `release.yml`. Se niega si `Sin publicar` está vacía.
- `release.yml`: publica la release con `drawio-icon-libraries.zip` y las notas del CHANGELOG.

## Git

- Ramas desde `main`: `feat/lib-<librería>`, `feat/<tema>`, `fix/<descripción>`, o la rama personal del contribuidor.
- Commits en español con [Conventional Commits](https://www.conventionalcommits.org/es/):
  `feat(icons): …`, `feat(fabric): …`, `fix(scripts): …`, `docs: …`, `ci: …`, `build: …`, `chore: …`.
- Los cambios llegan a `main` por Pull Request; la CI debe pasar en verde.
