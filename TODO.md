# Pendientes · Plan de mejora

Lista de trabajo para dejar el proyecto reproducible, ligero y entendible por cualquier desarrollador.
Las etapas están ordenadas por **dependencias**, no por gravedad: varias tareas tocan los mismos
archivos y hacerlas en otro orden obliga a repetirlas.

```
Etapa 0 ──> Etapa 1 ──> Etapa 2 ──> Etapa 3 ──> Etapa 5 ──> Etapa 6
                              └──> Etapa 4 (paralela, trabajo de contenido)
```

| Etapa | Qué | Esfuerzo | Bloqueada por | Estado |
|---|---|---|---|---|
| 0 | Validador + tag de seguridad | ½ día | — | ✅ |
| 1 | `build.py` + manifiesto | 1–2 días | 0 | ✅ |
| 2 | Títulos limpios | ½ día | 1 | ✅ |
| 3 | Borrar peso y notebooks | ½ día | 1 | ✅ |
| 4 | Iconos raster → vectorial | variable | — (paralela) | ✅ |
| 5 | CI + releases | ½ día | 0, 2 | ✅ (falta 1.ª release) |
| 6 | Documentación | 1 día | 1, 3 | ✅ |

Total aproximado: **4–5 días** de trabajo efectivo, más lo que tarde conseguir los SVG vectoriales de la etapa 4.

---

## Diagnóstico de partida (05-10-2026)

Estado del repo en el commit `8110279`, medido con un script de validación:

- 30 librerías, 4.511 archivos, ~60 MB sin `.git`.
- ✅ Las 30 librerías son XML válido; todos los ítems tienen `w=64`, `h=64`, `aspect="fixed"`; ningún SVG corrupto; sin títulos duplicados dentro de una misma librería.
- ❌ **27 iconos son raster** (PNG embebido en `<image>` dentro del SVG): 25 de Office 365 (65–478 KB cada uno, `Office 365.xml` pesa 5 MB), "Windows" en Operating Systems (865 KB), "Micronaut" en Programming.
- ❌ **628 títulos crudos**: 511 en las 20 librerías Azure, que usan el nombre de archivo (`00028-icon-service-Batch-AI`); 71 en Fabric con sufijo ` 48 item` / ` 48 color` / ` 48 non-item` / ` 48 items`; 46 en Dynamics 365 y Power Platform con sufijo ` scalable`.
- ❌ `svg/Fabric/png/` y `svg/Fabric/svg all/` = 3.010 archivos, 33 MB, sin ningún uso en los scripts.
- ❌ 1.741 rutas fijas `C:\Users\WIRBI\...` en 31 notebooks; el mismo código copiado ~30 veces.
- ❌ `scripts/Fabric/remove.ipynb` hace `os.remove` sobre ruta fija sin confirmación.
- ❌ README lista `lxml` y `cairosvg` como requisitos, pero ningún notebook los usa; la dependencia real es WSL + Inkscape + Pillow y no se menciona.
- ❌ README promete "Jupyter or CLI": no existe CLI. La checklist cita `docs/SOURCES.md` y una CI: no existen `docs/` ni `.github/`.
- ⚠️ 55 de 432 iconos Azure aparecen en 2+ librerías (probablemente intencional, las categorías de Microsoft se solapan).
- ⚠️ Comentarios desactualizados en notebooks (p. ej. `Programming.ipynb` dice "Office 365" y "18x18" cuando usa `SVG_96`).
- ⚠️ `README.es.md` solo se comparó por número de líneas (164 vs 167), no por contenido.
- ❌ **Saltos de línea dependientes del SO**: el notebook escribía los SVG normalizados con `tree.write(ruta)` (modo texto → CRLF en Windows) y el XML embebía esos bytes CRLF, mientras git guarda los SVG con LF. Empaquetar en Linux daba XML distintos que en Windows. *(Detectado en la etapa 1.)*
- ❌ El `.gitignore` de plantilla ignora `lib/`: un paquete `scripts/lib/` nunca se commitearía. *(Detectado en la etapa 1; el paquete se llama `scripts/iconlib/`.)*

---

## Etapa 0 · Preparación y red de seguridad

**Objetivo:** poder demostrar que ninguna etapa posterior rompe los iconos.

- [x] Crear rama `feat/pipeline-refactor`.
- [x] Etiquetar el estado actual: `git tag v0-legacy` (local, sin push).
- [x] Crear `scripts/validate.py` que, por cada `libraries/**/*.xml`, verifique:
  - [x] Envoltorio `<mxlibrary>` y JSON válido.
  - [x] Cada ítem: `w=64`, `h=64`, `aspect="fixed"`, `data:image/svg+xml;base64,...`.
  - [x] El SVG decodificado se parsea.
  - [x] Título no vacío, sin patrón `^\d+-icon-service-`, sin sufijos ` scalable` / ` 48 <variante>`, sin `.svg`.
  - [x] Sin `<image` embebido (raster), con **lista blanca temporal** para los 27 conocidos.
  - [x] Sin títulos duplicados dentro de la librería.
- [x] Que imprima un resumen y salga con código ≠ 0 si algo falla.

**Hecho cuando:** `python scripts/validate.py` corre sobre el repo actual y reporta la línea base: 0 XML inválidos, 27 raster (en lista blanca), 628 títulos crudos.

✅ **Completada.** Resultado sobre `v0-legacy`: 30 librerías, 717 ítems; formato/tamaño/svg/duplicados = 0; raster permitido = 27; títulos crudos = 628 (511 Azure + 71 Fabric + 46 `scalable`). Sale con código 1 hasta que se complete la etapa 2.

---

## Etapa 1 · Un solo script parametrizado

**Objetivo:** reemplazar los 31 notebooks por una herramienta de línea de comandos que cualquiera pueda ejecutar en cualquier sistema.

- [x] Crear `libraries.json` (manifiesto) con una entrada por librería:
  ```json
  {
    "name": "Azure Compute",
    "source": "svg/Azure/Azure Compute/SVG_18",
    "normalized": "svg/Azure/Azure Compute/SVG_64",
    "output": "libraries/Azure/Azure Compute/Azure Compute.xml",
    "title_rules": ["strip_azure_prefix", "dash_to_space"]
  }
  ```
- [x] Crear `scripts/build.py` con subcomandos (`list`, `normalize`, `pack`, `all`; modo manifiesto con `-l NOMBRE` o modo suelto con `--input/--output`):
  - [x] `normalize` → SVG a 64×64 centrados (Inkscape en `PATH`, `--inkscape` o `$INKSCAPE`).
  - [x] `pack` → genera el mxlibrary XML (solo stdlib). `pack --check` no escribe y falla si algún XML no coincide con sus SVG (para CI).
  - [x] `all` → `normalize` + `pack`.
  - [x] Flags `--dry-run` y `--verbose`.
- [x] Mover la lógica común a `scripts/iconlib/` (no `lib/`, que está en `.gitignore`): `manifest.py`, `svg_normalize.py`, `mxlibrary.py`, `titles.py`.
- [x] Añadir `requirements.txt` y `pyproject.toml` mínimos (solo Pillow; `pack`/`validate`/`compare` usan stdlib).
- [x] Añadir `scripts/compare.py`: compara ítem a ítem `libraries/` contra una referencia git (`--ref v0-legacy`) y clasifica cada SVG en idéntico / solo EOL / DISTINTO.
- [x] Saltos de línea deterministas (adelantado de la etapa 3):
  - [x] `pack` convierte CRLF → LF antes de codificar en base64.
  - [x] `normalize` escribe en binario (siempre LF).
  - [x] `.gitattributes`: `*.svg text eol=lf` y `libraries/**/*.xml text eol=lf -diff`.

**Decisiones pendientes (del mantenedor):**

- [x] **Renderizador para medir el bbox → Inkscape en `PATH`** (decidido 05-10-2026). Se elimina la dependencia de `wsl bash -lc`; funciona en Linux, macOS y Windows. Se descarta `cairosvg`.
- [x] **Carpetas `SVG_64/` → se conservan** (decidido 05-10-2026), renombradas a un patrón uniforme en la etapa 3. Motivos:
  - Separan el paso pesado (`normalize`, requiere Inkscape, ~1 s/icono) del ligero (`pack`, solo stdlib): cambiar un título o añadir una librería no exige Inkscape.
  - Coste bajo: 717 archivos, ~6,5 MB.
  - Los usuarios pueden descargar iconos sueltos de 64×64 desde GitHub.
  - Los cambios de normalización se revisan como diff de SVG legible.
  - Riesgo de desincronización `SVG_64/` ↔ XML: cubierto por la comprobación obligatoria de la etapa 5.

**Hecho cuando:** `python scripts/build.py pack` regenera las 30 librerías y el SVG decodificado de cada ítem es idéntico byte a byte al de `v0-legacy` **tras normalizar CRLF → LF**, sin cambios de título, tamaño ni número de ítems.

✅ **Completada.** Resultados:
- `compare.py --ref v0-legacy`: 717/717 SVG «solo EOL», 0 distintos, 0 títulos/atributos cambiados.
- `build.py pack --check`: 30 librerías al día.
- Geometría de `normalize`: sustituyendo la medición de Inkscape por el bbox recuperado del `transform` de cada SVG commiteado, 717/717 salidas idénticas byte a byte.
- ✅ ~~Sin probar la medición real con Inkscape~~ → probada en la etapa 2 (21/21 idénticos con Inkscape 1.4.4). Re-normalizar con otra versión de Inkscape **nunca** será idéntico byte a byte (el raster cambia el bbox → cambian los decimales del `transform`): cualquier prueba futura de `normalize` debe usar tolerancia numérica.
- Revisión adversarial (4 enfoques: fidelidad, multiplataforma, CLI, robustez; 2 verificadores por hallazgo): 26 hallazgos confirmados (~13 problemas distintos), todos corregidos y con prueba. Entre ellos: `normalize` fallaba siempre por un argumento ausente; `--dry-run` exigía Inkscape; normalizar un SVG ya normalizado lo deformaba sin avisar; SVG huérfanos en `SVG_64/` se seguían empaquetando (ahora `pack` falla y `normalize --prune` los elimina); `--inkscape` inválido se ignoraba; claves erróneas en `libraries.json` daban traceback.
- Los XML regenerados (solo cambian CRLF → LF) **no se commitean en esta etapa**: se commitean una sola vez en la etapa 2 junto con los títulos limpios.

---

## Etapa 2 · Limpieza de títulos y regeneración

**Objetivo:** que el nombre que ve el usuario en Draw.io sea legible y buscable.

- [ ] Implementar en `scripts/lib/titles.py` las reglas:
  - [x] `strip_azure_prefix`: `^\d+-icon-service-` → quitar (Azure, 511 ítems / 432 iconos únicos).
  - [x] `dash_to_space`: `-` → espacio (Azure).
  - [x] `strip_scalable`: ` scalable` y ` scalable (1)` → quitar (Dynamics 365, Power Platform; 47 ítems).
  - [x] `split_camel_case`: `BusinessCentral` → `Business Central`, `AIBuilder` → `AI Builder`, `Dynamics365` → `Dynamics 365` (Dynamics 365, Power Platform). *Añadida: sin ella Draw.io no encuentra «Business Central».*
  - [x] `fabric_suffix`: ` 48 item` → quitar; ` 48 color` / ` 48 non-item` / ` 48 items` → `(color)` / `(non-item)` / `(items)` (Fabric, 71 ítems). *Cambiada: quitar todo el sufijo dejaba títulos repetidos con iconos distintos (`data warehouse`, `event house`, `metric sets`).*
  - [x] `strip_color_icon`: ` color icon` → quitar (Entra ID, 6 ítems). *Añadida.*
  - [x] `title_overrides` en `libraries.json` para títulos que ninguna regla puede deducir: `00330-icon-service-Workspaces` → `Workspaces (Virtual Desktop)` (Microsoft tiene dos iconos distintos llamados «Workspaces»; el 00330 es el de Azure Virtual Desktop, junto a Host Pools y Application Group).
- [x] Asignar reglas por librería en `libraries.json`.
- [x] Regenerar todo con `python scripts/build.py pack` (no requiere Inkscape) y commitear los 30 XML: incluye los títulos limpios y el paso CRLF → LF pendiente de la etapa 1.
- [x] Confirmar con `python scripts/compare.py --ref v0-legacy`: solo cambian títulos y EOL, 0 SVG distintos.
- [ ] Revisar manualmente 3–4 librerías en Draw.io (capturas para el PR). *Pendiente del mantenedor: requiere la app.*
- [ ] *Opcional:* títulos de Fabric en minúsculas (`kql database`, `power bi (color)`) y algunos de Programming (`Java script`, `Type script`, `Next js`, `Css`, `Mysql`). No afectan a la búsqueda (no distingue mayúsculas); corregirlos requiere nombres a mano vía `title_overrides` o renombrar los SVG.

**Hecho cuando:** `validate.py` reporta 0 títulos crudos en las 30 librerías y buscar "Kubernetes" en Draw.io encuentra el icono.

✅ **Completada** (salvo la revisión visual en Draw.io). Resultados:
- `validate.py`: **OK** — 0 errores de formato, tamaño, SVG, títulos y duplicados; 27 raster en lista blanca.
- `build.py pack --check`: 30 librerías al día.
- `compare.py --ref v0-legacy`: 635 títulos cambiados, 717/717 SVG solo EOL, 0 SVG distintos, 0 cambios de w/h/aspect ni de número de ítems.
- `validate.py` detecta además ` scalable (1)` y ` color icon`.
- `normalize` probado con Inkscape 1.4.4 real (instalado con winget): Developing, Azure Blockchain y Power Platform → 21/21 SVG idénticos byte a byte a los commiteados. Velocidad: 1–4 s por icono.

---

## Etapa 3 · Reducir peso y eliminar código muerto

**Objetivo:** que clonar y navegar el repo sea rápido y no haya nada que confunda.

- [x] Borrar `svg/Fabric/png/` y `svg/Fabric/svg all/` (3.010 archivos, 33 MB). Origen documentado en `docs/SOURCES.md`.
- [x] Borrar `scripts/Fabric/remove.ipynb`.
- [x] Borrar los 30 notebooks ya reemplazados por `build.py` (no se conserva ninguno: `build.py` cubre todo su código; siguen disponibles en el tag `v0-legacy`).
- [x] Unificar la estructura de `svg/` a un patrón único: `svg/<librería>/source/` (originales, antes `SVG_18` / `SVG_48` / `SVG_96`) y `svg/<librería>/64/` (normalizados, commiteados). Fabric pasa de `svg/Fabric/svg/SVG_48` a `svg/Fabric/source`.
- [x] Crear `docs/SOURCES.md` con el paquete de origen de cada librería, extraído de las rutas de los notebooks (URLs y licencias pendientes de verificar en la etapa 6).
- [x] ~~Añadir `.gitattributes`~~ → hecho en la etapa 1.

**Punto de decisión (no es un paso):**

- [x] Borrar del árbol **no** reduce el tamaño del clon; los 33 MB siguen en `.git`. → **Decidido: sí** (05-10-2026). Historial reescrito con `git filter-repo --invert-paths --path svg/Fabric/png --path "svg/Fabric/svg all"`.
  - Respaldo previo: `C:\GitHub\drawio-icon-libraries-backup-2026-10-05.bundle` (todas las ramas y tags; restaurar con `git clone <bundle>`).
  - Verificado: los 10 commits reescritos tienen el mismo árbol (salvo las dos carpetas) y los mismos autor, fecha y mensaje; ningún commit contiene ya esas rutas.
  - [x] Force-push de `main` (`8110279` → `497c510`) y `feat/pipeline-refactor` (`a41568a` → `02cad3d`) hecho por el mantenedor el 05-10-2026. Cualquier otro clon del repo debe volver a clonarse.

**Hecho cuando:** repo sin `.git` < 20 MB; `git ls-files | wc -l` < 1.500.

✅ **Completada.** Resultados:
- `git ls-files`: 4.511 → **1.484** archivos ✅.
- `.git`: 39 MB → **14 MB** (pack de 32,6 → 12,9 MiB) ✅.
- Repo sin `.git`: 60 → 27 MB tras esta etapa; **13 MB** tras la etapa 4 ✅ (objetivo 20 MB).
- `pack --check`, `validate.py` y `compare.py --ref v0-legacy`: OK.

Comando de force-push (protegido: falla si alguien más ha subido cambios desde `8110279` / `a41568a`):

```bash
git push --force-with-lease=main:81102793a764f8040699fd3b6ed7ce01ecc6be60 \
         --force-with-lease=feat/pipeline-refactor:a41568a48ed027ed8253ac79aacd40a77d03539b \
         origin main feat/pipeline-refactor
```

---

## Etapa 4 · Iconos raster → vectorial (paralela)

**Objetivo:** cumplir la promesa del README ("100% vectorial").

Iconos afectados (27):

- [x] **Office 365 (25):** Access, Clipchamp, Defender, Editor, Excel, Exchange, Family Safety, Forms, OneDrive, OneNote, Outlook, Planner, Power Apps, Power Automate, Power BI, PowerPoint, Project, Publisher, Sharepoint, Stream, Sway, Teams, To Do, Visio, Word.
- [x] **Operating Systems (1):** Windows.
- [x] **Programming (1):** Micronaut.

Tareas:

- [x] **Verificar disponibilidad** de fuentes vectoriales. Evaluadas (detalle en `docs/SOURCES.md`):
  - Fluent UI «Office brand icons» (CDN oficial): **descartada** por licencia (solo para desarrollar Add-ins/SharePoint) y diseño 2019.
  - Microsoft 365 architecture icons: licencia válida, pero solo iconos de contenido, sin logotipos.
  - DamoBird365/microsoft-cloud-icons: mismo diseño 2025, vectorial, **sin licencia ni procedencia declarada** → aceptada por el mantenedor para 23 iconos (los 20 iniciales + Power Apps, Power Automate y Power BI, que pasan al diseño 2025).
  - Wikimedia Commons (dominio público, atribuidos a Microsoft): Exchange y Windows.
  - micronaut.io (logo oficial, uso comunitario permitido): Micronaut.
- [x] Editor: sus PNG eran solo sombras → se eliminaron las capas `<image>` del mismo SVG (cambia < 0,3 % de los píxeles).
- [x] Reemplazar y regenerar con `build.py all` (Inkscape 1.4.4): cambian exactamente los 27 SVG; los otros 690 salen idénticos byte a byte.
- [x] Revisión visual de los 27 normalizados a 64×64: mismo diseño, centrados y nítidos.
- [x] Lista blanca del validador vaciada.
- [ ] *Opcional:* sustituir los 23 de DamoBird365 si aparece una fuente oficial de Microsoft con licencia clara.
- [x] Power Apps, Power Automate y Power BI de Office 365 pasados al diseño 2025 de DamoBird365 (decisión del mantenedor).

**Hecho cuando:** `Office 365.xml` < 500 KB y lista blanca vacía (o con justificación escrita por cada excepción).

✅ **Completada.** Resultados:
- `Office 365.xml`: 5,0 MB → **262 KB** ✅. `Operating Systems.xml`: 1,2 MB → 75 KB. `Programming.xml`: 394 → 356 KB.
- Lista blanca vacía; `validate.py` OK con 0 raster ✅.
- Repo sin `.git`: 27 → **13 MB** (cumple también el objetivo de la etapa 3, < 20 MB).
- `pack --check` OK; `compare.py`: 27 SVG distintos (los sustituidos a propósito), 690 idénticos, 0 títulos cambiados.

---

## Etapa 5 · Integración continua y releases

**Objetivo:** que los problemas de las etapas 2 y 4 no vuelvan, y que descargar sea fiable.

- [x] `.github/workflows/validate.yml`: en cada PR, push a `main` y manual; Ubuntu con Python 3.9 (mínimo declarado) y 3.x. Ejecuta `validate.py`, `build.py pack --check` y `package.py`.
- [x] `.github/workflows/release.yml`: al subir un tag `v*`, valida, genera el ZIP y publica la GitHub Release con `gh release create --generate-notes`. *Cambio respecto al plan:* el ZIP se llama siempre `drawio-icon-libraries.zip` (no `…-<tag>.zip`) para que `releases/latest/download/drawio-icon-libraries.zip` sea un enlace fijo a la última versión.
- [x] `scripts/package.py`: ZIP con `libraries/`, `LICENSE` y `SOURCES.md`; reproducible en una misma plataforma (orden y fechas fijos).
- [x] Reemplazar en los dos README el botón de `download-directory.github.io` por la descarga directa de la última release; añadidas insignias de versión y de estado de la CI.
- [x] **Obligatorio:** job en Ubuntu que ejecute `python scripts/build.py pack --check` y falle si algún XML difiere de lo que generan sus SVG de 64×64 (no requiere Inkscape). Depende de que `pack` convierta CRLF → LF y de `.gitattributes`: **no eliminar ninguno de los dos**, o el job dará falsos positivos según el SO.
- [ ] **Pendiente del mantenedor:** subir la rama, abrir el PR a `main`, comprobar que la CI pasa, hacer merge y crear el tag: `git tag v1.0.0 && git push origin v1.0.0`. Hasta que exista la primera release, el botón de descarga del README devuelve 404.

**Hecho cuando:** un PR con un título crudo o un `<image>` nuevo aparece en rojo; existe la release `v1.0.0` con el ZIP.

✅ **Completada en local** (falta la ejecución real en GitHub). Verificado:
- `actionlint` 1.7.12: sin errores en los dos workflows.
- Simulación de la CI en un clon limpio en Linux (WSL): caso limpio OK; **en rojo** con (1) un icono nuevo con título crudo, (2) un icono con `<image>` raster y (3) un XML editado a mano sin tocar sus SVG.
- `package.py`: 32 archivos, ~840 KB, mismos bytes en dos ejecuciones seguidas.

---

## Etapa 6 · Documentación para el siguiente desarrollador

**Objetivo:** que alguien sin contexto pueda instalar, generar y contribuir en menos de 15 minutos.

- [x] **README.md**
  - [x] Corregir requisitos: Python 3.9+ para todo; Inkscape 1.x + Pillow solo para `normalize`. Fuera `lxml`, `cairosvg`, Jupyter y WSL (título, insignia e introducción).
  - [x] Sección «Build the libraries yourself» con los comandos reales de `build.py`.
  - [x] Árbol de la estructura del repo.
  - [x] Mantener el aviso de marcas registradas (ahora enlaza a `docs/SOURCES.md`).
  - [x] Lista de librerías como tabla con el número de iconos (30 librerías, 717 iconos).
  - [x] Índice con anclajes explícitos (`<a id>`): con emoji al inicio del título, el anclaje automático de GitHub no coincide con `#requirements`/`#download`, así que los enlaces del índice anterior probablemente fallaban en GitHub.
- [x] **CONTRIBUTING.md** (en español, como el código y el CLI): requisitos, estructura, comandos, añadir iconos, añadir una librería, reglas y `title_overrides`, checklist del PR, ramas y commits, publicar versión, problemas frecuentes. El README conserva un resumen de 4 pasos y enlaza aquí.
- [x] **docs/SOURCES.md**: las 5 URL oficiales verificadas (responden). Queda pendiente anotar versión y fecha de descarga de cada paquete.
- [x] **docs/ARCHITECTURE.md**: flujo, algoritmo de normalización, formato mxlibrary, determinismo (CRLF/LF), por qué se commitean los SVG de 64×64, validaciones, CI y decisiones menores.
- [x] **README.es.md**: misma estructura y contenido que README.md (antes ya era una traducción fiel; ahora se reescribió en paralelo).
- [x] **CHANGELOG.md** con `v1.0.0` (sin fecha hasta publicar).
- [x] Nota en el README sobre los iconos Azure presentes en 2+ librerías.

**Hecho cuando:** un compañero sigue el README en una máquina limpia y regenera una librería sin preguntar nada.

✅ **Completada.** Verificado con un agente que hizo de desarrollador nuevo sobre un clon limpio, siguiendo solo la documentación: sin bloqueos; regeneró librerías, añadió un icono y una librería nueva, y usó `--prune`. Detectó 18 problemas, todos corregidos en `a7cc56d`. El más grave: la ruta `svg/<librería>/source/` de los docs no existía para Azure, Fabric ni Dynamics, y un icono copiado ahí se perdía con todas las comprobaciones en verde. Ahora `pack` falla en ese caso y `build.py list -v` muestra la carpeta correcta.

Pendiente fuera de esta etapa:
- [ ] Anotar versión y fecha de descarga de cada paquete en `docs/SOURCES.md`.
- [ ] Subir el tag `v0-legacy` si se quiere que los enlaces de CHANGELOG/SOURCES a los notebooks funcionen en GitHub: `git push origin v0-legacy`.
