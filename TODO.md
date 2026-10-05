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
| 1 | `build.py` + manifiesto | 1–2 días | 0 | ⬜ |
| 2 | Títulos limpios | ½ día | 1 | ⬜ |
| 3 | Borrar peso y notebooks | ½ día | 1 | ⬜ |
| 4 | Iconos raster → vectorial | variable | — (paralela) | ⬜ |
| 5 | CI + releases | ½ día | 0, 2 | ⬜ |
| 6 | Documentación | 1 día | 1, 3 | ⬜ |

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

- [ ] Crear `libraries.json` (manifiesto) con una entrada por librería:
  ```json
  {
    "name": "Azure Compute",
    "source": "svg/Azure/Azure Compute/SVG_18",
    "output": "libraries/Azure/Azure Compute/Azure Compute.xml",
    "title_rules": ["strip_azure_prefix", "dash_to_space"]
  }
  ```
- [ ] Crear `scripts/build.py` con subcomandos:
  - [ ] `normalize --input DIR --output DIR [--padding 3]` → SVG a 64×64 centrados.
  - [ ] `pack --input DIR --output FILE --title-rules ...` → genera el mxlibrary XML.
  - [ ] `all` → recorre el manifiesto completo.
  - [ ] Flags `--dry-run` y `--verbose`.
- [ ] Mover la lógica común a `scripts/lib/`: `svg_normalize.py`, `mxlibrary.py`, `titles.py`.
- [ ] Añadir `requirements.txt` y `pyproject.toml` mínimos.
- [ ] Añadir `scripts/compare.py` (o un test) que compare el SVG decodificado de cada ítem entre dos XML.

**Decisiones pendientes (del mantenedor):**

- [ ] **Renderizador para medir el bbox.** Hoy se llama a Inkscape vía `wsl bash -lc`, lo que ata el proyecto a Windows+WSL.
  - (a) Inkscape en `PATH` — funciona en Linux, macOS y Windows sin WSL. *Recomendado.*
  - (b) `cairosvg` — coincide con lo que dice el README y quita Inkscape, pero rasteriza filtros/fuentes distinto: los bboxes pueden cambiar. **No probado**, no se garantiza resultado idéntico.
- [ ] **Conservar o no las carpetas `SVG_64/`.** Son salida regenerable (el XML ya las embebe). Quitarlas reduce `svg/` a la mitad, pero se pierde la inspección directa de los iconos sin abrir Draw.io.

**Hecho cuando:** `python scripts/build.py all` regenera las 30 librerías y el SVG decodificado de cada ítem es **byte a byte idéntico** al actual (los títulos pueden diferir).

---

## Etapa 2 · Limpieza de títulos y regeneración

**Objetivo:** que el nombre que ve el usuario en Draw.io sea legible y buscable.

- [ ] Implementar en `scripts/lib/titles.py` las reglas:
  - [ ] `^\d+-icon-service-` → quitar (Azure, 511 ítems / 432 iconos únicos).
  - [ ] `-` → espacio.
  - [ ] ` scalable$` → quitar (Dynamics 365, Power Platform; 46 ítems).
  - [ ] ` 48( \S+)?$` → quitar (Fabric: ` 48 item`, ` 48 color`, ` 48 non-item`, ` 48 items`; 71 ítems).
- [ ] Asignar reglas por librería en `libraries.json`.
- [ ] Regenerar todo con `build.py all`.
- [ ] Revisar manualmente 3–4 librerías en Draw.io (capturas para el PR).

**Hecho cuando:** `validate.py` reporta 0 títulos crudos en las 30 librerías y buscar "Kubernetes" en Draw.io encuentra el icono.

---

## Etapa 3 · Reducir peso y eliminar código muerto

**Objetivo:** que clonar y navegar el repo sea rápido y no haya nada que confunda.

- [ ] Borrar `svg/Fabric/png/` y `svg/Fabric/svg all/` (3.010 archivos, 33 MB). Documentar en `docs/SOURCES.md` el enlace al paquete oficial de Microsoft del que salieron.
- [ ] Borrar `scripts/Fabric/remove.ipynb`.
- [ ] Borrar los 30 notebooks ya reemplazados por `build.py`. Si se quiere conservar uno como tutorial, dejar **un solo** `docs/notebooks/ejemplo.ipynb` sin salidas (`nbstripout`).
- [ ] Unificar la estructura de `svg/` a un patrón único: `svg/<categoría>/source/` (original) y, si se decidió conservarla, `svg/<categoría>/64/`.
- [ ] Añadir `.gitattributes` marcando `libraries/**/*.xml` como `-diff` (evita diffs gigantes de base64).

**Punto de decisión (no es un paso):**

- [ ] Borrar del árbol **no** reduce el tamaño del clon; los 33 MB siguen en `.git`. El repo tiene 5 commits y un solo autor: `git filter-repo` es viable ahora y doloroso después. Requiere force-push. Decidir sí/no.

**Hecho cuando:** repo sin `.git` < 20 MB; `git ls-files | wc -l` < 1.500.

---

## Etapa 4 · Iconos raster → vectorial (paralela)

**Objetivo:** cumplir la promesa del README ("100% vectorial").

Iconos afectados (27):

- [ ] **Office 365 (25):** Access, Clipchamp, Defender, Editor, Excel, Exchange, Family Safety, Forms, OneDrive, OneNote, Outlook, Planner, Power Apps, Power Automate, Power BI, PowerPoint, Project, Publisher, Sharepoint, Stream, Sway, Teams, To Do, Visio, Word.
- [ ] **Operating Systems (1):** Windows.
- [ ] **Programming (1):** Micronaut.

Tareas:

- [ ] **Verificar disponibilidad** de fuentes vectoriales oficiales (Microsoft Learn publica SVG de M365; Micronaut tiene logo SVG en su repositorio). No se asume que existan todas.
- [ ] Reemplazar los que se encuentren y regenerar con `build.py`.
- [ ] Los que no se encuentren: documentarlo en `docs/SOURCES.md` y mantenerlos en la lista blanca del validador con justificación.
- [ ] Ir vaciando la lista blanca según se resuelvan.

**Hecho cuando:** `Office 365.xml` < 500 KB y lista blanca vacía (o con justificación escrita por cada excepción).

---

## Etapa 5 · Integración continua y releases

**Objetivo:** que los problemas de las etapas 2 y 4 no vuelvan, y que descargar sea fiable.

- [ ] `.github/workflows/validate.yml`: en cada PR y push a `main`, ejecutar `scripts/validate.py`.
- [ ] `.github/workflows/release.yml`: al crear un tag `v*`, comprimir `libraries/` en `drawio-icon-libraries-<tag>.zip` y adjuntarlo a la GitHub Release.
- [ ] Reemplazar en el README el botón de `download-directory.github.io` (servicio de terceros) por el enlace a la última release.
- [ ] Opcional: job que regenere las librerías y falle si el resultado difiere del commit (garantiza que `libraries/` siempre sale de `svg/`).

**Hecho cuando:** un PR con un título crudo o un `<image>` nuevo aparece en rojo; existe la release `v1.0.0` con el ZIP.

---

## Etapa 6 · Documentación para el siguiente desarrollador

**Objetivo:** que alguien sin contexto pueda instalar, generar y contribuir en menos de 15 minutos.

- [ ] **README.md**
  - [ ] Corregir requisitos (Inkscape o cairosvg según etapa 1, Pillow; quitar `lxml`).
  - [ ] Sección "Uso rápido" con los comandos reales de `build.py`.
  - [ ] Sección "Estructura del repo" con un árbol.
  - [ ] Mantener el aviso de marcas registradas.
- [ ] **CONTRIBUTING.md**: sacar del README el flujo Fork → Branch → PR y la checklist; explicar cómo añadir una librería nueva (= una entrada en `libraries.json` + carpeta en `svg/`).
- [ ] **docs/SOURCES.md**: por cada librería, URL de origen, fecha de descarga, versión y licencia.
- [ ] **docs/ARCHITECTURE.md** (corto): cómo funciona la normalización (bbox por render → escala → padding → viewBox 64×64) y el formato mxlibrary.
- [ ] **README.es.md**: diff de contenido real contra README.md y sincronizar. Decidir si mantiene todo o solo lo esencial con enlace al inglés.
- [ ] **CHANGELOG.md** empezando en `v1.0.0`.
- [ ] Nota opcional en el README sobre los 55 iconos Azure presentes en 2+ librerías.

**Hecho cuando:** un compañero sigue el README en una máquina limpia y regenera una librería sin preguntar nada.
