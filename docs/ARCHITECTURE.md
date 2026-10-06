# Arquitectura

Cómo se generan las librerías y por qué el pipeline está diseñado así. Para el «cómo hago X»
práctico, ve a [CONTRIBUTING.md](../CONTRIBUTING.md).

## Flujo

```
svg/<lib>/source/*.svg ──normalize──▶ svg/<lib>/64/*.svg ──pack──▶ libraries/<…>.xml ──package──▶ dist/drawio-icon-libraries.zip
   (proveedor)          Inkscape+Pillow   (commiteado)      stdlib     (commiteado)      stdlib        (asset de la release)
```

Todo lo gobierna [libraries.json](../libraries.json): una entrada por librería con sus carpetas
`source` y `normalized`, el `.xml` de salida y las reglas de título.

| Paso | Script | Dependencias | Lento |
|---|---|---|---|
| `normalize` | `scripts/build.py` → `iconlib/svg_normalize.py` | Inkscape 1.x, Pillow | sí (1–4 s/icono) |
| `pack` | `scripts/build.py` → `iconlib/mxlibrary.py`, `iconlib/titles.py` | ninguna | no |
| validar | `scripts/validate.py` | ninguna | no |
| comparar | `scripts/compare.py` | git | no |
| empaquetar | `scripts/package.py` | ninguna | no |
| README | `scripts/readme.py` | ninguna | no |

## Normalización a 64×64

Los proveedores entregan SVG de tamaños y márgenes distintos (p. ej. Azure 18×18, Office 365 24×24,
Programming 32×32, Fabric 48×48, Dynamics 365 96×96, y algunos `viewBox` arbitrarios). `normalize` los lleva a un lienzo común **sin rasterizar el resultado**:

1. **Medir.** Inkscape exporta el SVG a PNG (1024 px de ancho, área de página). Pillow calcula la caja
   del contenido visible: píxeles con alfa ≥ 80, para ignorar sombras suaves.
2. **Convertir** esa caja de píxeles a unidades del `viewBox` original.
3. **Escalar y centrar.** Escala `s` para que la caja quepa en 64×64 con 3 px de margen
   (`s = min(58/ancho, 58/alto)`), centrada en ambos ejes.
4. **Envolver** el contenido (salvo `<defs>`) en
   `<g data-normalized="1" transform="translate(centro) scale(s) translate(-caja)">` y fijar
   `viewBox="0 0 64 64"`, `width`/`height` = 64.

El resultado sigue siendo 100 % vectorial; el PNG solo se usa para medir. Parámetros
(`padding`, `alpha_cutoff`, `render_px`) en `defaults` de `libraries.json` o por línea de comandos.

`normalize` rechaza un SVG que ya tenga `<g data-normalized="1">`: re-normalizarlo sustituiría el
`transform` sin componerlo con el anterior y deformaría el icono sin avisar.

## Formato mxlibrary

Un `.xml` de Draw.io es un array JSON envuelto en `<mxlibrary>`:

```xml
<mxlibrary>[{"data":"data:image/svg+xml;base64,…","w":64,"h":64,"title":"Batch AI","aspect":"fixed"}, …]</mxlibrary>
```

- Ítems ordenados por nombre de archivo sin distinguir mayúsculas.
- `w`/`h` salen del `viewBox` del SVG normalizado (siempre 64).
- `title`: nombre del archivo con `_` → espacio, más las `title_rules` y `title_overrides` de la librería.
- JSON compacto (`separators=(",", ":")`, `ensure_ascii=False`), sin salto de línea final.

## Determinismo: por qué el mismo commit genera los mismos bytes en cualquier SO

`pack --check` (en la CI) regenera los `.xml` y los compara byte a byte con los commiteados.
Para que no dé falsos positivos según el sistema:

- **`pack` convierte CRLF → LF** en cada SVG antes de codificarlo en base64.
- **`normalize` escribe en binario.** `ElementTree.write(ruta)` abre en modo texto y en Windows
  convertía el salto de línea de la declaración XML en CRLF (era el origen de la diferencia
  entre Windows y Linux en las librerías originales).
- **`.gitattributes`** fija `eol=lf` en `*.svg` y `libraries/**/*.xml`.

No elimines ninguna de las tres piezas: cualquiera de ellas por separado deja algún caso sin cubrir.

La normalización **no** es reproducible entre versiones de Inkscape: el rasterizado puede mover un
píxel la caja medida y cambiar los decimales del `transform`. Con Inkscape 1.4.4 se re-normalizaron
115 iconos de 7 librerías (Developing, Azure Blockchain, Azure Web, Power Platform, Office 365,
Programming y Operating Systems) y salieron idénticos a los commiteados; con otra versión, compara con tolerancia numérica.

## Por qué se commitean los SVG de 64×64

Son salida regenerable, pero se guardan en el repo porque:

- Separan el paso pesado (`normalize`, Inkscape) del ligero (`pack`, solo Python): cambiar un título,
  revisar un PR o ejecutar la CI no requiere Inkscape.
- Los usuarios pueden descargar iconos sueltos de 64×64 desde GitHub.
- Un cambio en la normalización se revisa como diff de SVG legible, no como base64.

El riesgo de que `64/` y el `.xml` se desincronicen lo cubre `pack --check` en la CI. Además, `pack`
falla si `64/` tiene SVG sin original en `source/` o al revés (`all -l <librería> --prune` limpia los
huérfanos), y si hay SVG bajo `svg/` fuera de las carpetas declaradas en `libraries.json` (iconos
copiados a una carpeta equivocada, que si no quedarían fuera sin aviso).

## Validaciones

| Comprobación | Dónde | Falla si… |
|---|---|---|
| Formato | `validate.py` | falta `<mxlibrary>`, el JSON no es válido o un SVG no se puede leer |
| Tamaño | `validate.py` | algún ítem no es `w=64`, `h=64`, `aspect="fixed"` |
| Títulos | `validate.py` | título vacío, duplicado en la librería o con restos del nombre de archivo (`RAW_TITLE_PATTERNS`) |
| Raster | `validate.py` | un SVG embebe `<image>` y no está en `RASTER_ALLOWLIST` (vacía) |
| Sincronía | `build.py pack --check` | un `.xml` no coincide con lo que generan sus SVG de 64×64 |
| Carpetas | `build.py pack` | hay SVG huérfanos entre `source/` y `64/`, o SVG fuera de las carpetas del manifiesto |
| README | `readme.py --check` | la tabla, los enlaces a diagrams.net o los totales no coinciden con `libraries.json` |
| Regresiones | `compare.py --ref <ref>` | (manual) un icono cambia cuando no debería |

## CI y versiones

- [validate.yml](../.github/workflows/validate.yml): en cada PR y push a `main`, en Ubuntu con
  Python 3.14 (mínimo declarado) y 3.x (siempre la más reciente): `validate.py`, `pack --check`,
  `package.py` y `readme.py --check`.
- Enlaces «Open ↗» del README: `https://app.diagrams.net/?splash=0&clibs=U<url>` (parámetro oficial
  [`clibs`](https://www.drawio.com/doc/faq/supported-url-parameters)), con `<url>` = el `.xml` en
  `raw.githubusercontent.com/…/main/…` (permite CORS), codificada una sola vez para que diagrams.net use
  el nombre del archivo, ya decodificado, como título de la librería. Varias librerías se separan con `;`.
- [publish.yml](../.github/workflows/publish.yml) («Publicar versión», manual): calcula la versión
  siguiente desde el último tag, prepara `CHANGELOG.md` y `pyproject.toml` con `scripts/release.py`, hace
  commit en `main`, sube el tag (`git push --atomic`, ambos o ninguno) y llama a `release.yml`.
  Lo llama directamente porque un tag subido con el token de Actions no dispara otros workflows.
- [release.yml](../.github/workflows/release.yml): llamado por `publish.yml` o al subir a mano un tag
  `v*`. Valida, genera el ZIP y publica la release con las notas de esa versión del CHANGELOG. El ZIP
  tiene siempre el mismo nombre, así que `releases/latest/download/drawio-icon-libraries.zip` apunta
  siempre a la última versión.

## Instalador de escritorio (Windows)

`scripts/install-drawio-desktop.ps1` (lanzado con doble clic por `install-drawio-desktop.bat`, ambos dentro del
ZIP de la release) copia las librerías a una carpeta fija y las mantiene al día:

1. **Dónde instalar**, en este orden: `-InstallDir`; la carpeta guardada en
   `%LOCALAPPDATA%\drawio-icon-libraries\install-dir.txt` por una ejecución anterior; la carpeta desde la que
   Draw.io ya carga nuestras librerías (detectada leyendo, solo lectura, su localStorage); o
   `%LOCALAPPDATA%\drawio-icon-libraries\libraries`.
2. **Actualizar** es sobrescribir los `.xml` en esa carpeta: Draw.io guarda las librerías por ruta, así que al
   abrirse carga los archivos nuevos. Sin duplicados y sin pasos manuales.
3. **Primera vez**: abre la carpeta y Draw.io y pide importar cada `.xml` una vez con *Abrir biblioteca*.

**Por qué la primera importación no se automatiza** (investigado en el código de drawio-desktop 31.7, no lo
reabras sin una versión nueva de Draw.io que cambie esto):

- La app solo lee archivos locales «autorizados»: abiertos con su diálogo, pasados por línea de comandos o
  declarados en su configuración (Extras → Configuración). La CSP (`connect-src 'self'`) impide cargar
  librerías desde URLs, así que los enlaces «Open ↗» de la web no sirven en escritorio.
- `urlParams.json` (leído de la carpeta de trabajo al arrancar) sí llega a la página, pero Electron codifica la
  URL y el `;` que separa librerías en `clibs` llega como `%3B`: solo funciona con **una** librería.
- `defaultCustomLibraries` de la configuración solo se aplica a perfiles que nunca han abierto una librería, y
  la configuración vive en una base LevelDB interna que no se debe escribir desde fuera.
- Automatizarlo con el puerto de depuración de Chromium (inyectar JavaScript en Draw.io) se descartó: es
  inaceptable en un instalador y depende de detalles internos.

Lectura del estado de Draw.io: `%APPDATA%\draw.io\Local Storage\leveldb`. El registro `.log` se recompone
según el formato LevelDB (bloques de 32 KB con cabeceras de 7 bytes que pueden partir un valor); las tablas
`.ldb` suelen ir comprimidas (Snappy) y no se interpretan. Por eso el marcador `install-dir.txt` es la fuente
principal tras la primera ejecución. Posible mejora no verificada: la clave `libraries` de la configuración
añade una sección en «Más formas» con rutas locales autorizadas (30 casillas en un diálogo en vez de 30 diálogos).

## Decisiones menores

- El paquete se llama `scripts/iconlib/` y no `lib/` porque el `.gitignore` de plantilla de Python
  ignora `lib/`.
- `build.py` usa solo `argparse` y la biblioteca estándar; Pillow se importa de forma diferida dentro
  de `normalize`, para que el resto funcione sin dependencias.
- 55 de los 432 iconos de Azure aparecen en 2 o más librerías: Microsoft los clasifica en varias
  categorías y se respeta su agrupación.
