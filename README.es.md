<p align="right">
  <a href="README.md"><img src="https://img.shields.io/badge/lang-EN-blue" alt="English"></a>
  <a href="README.es.md"><img src="https://img.shields.io/badge/lang-ES-red" alt="Español"></a>
</p>

# Draw.io Icon Libraries (XML) · SVG → 64×64 · Python
[![Made with Python](https://img.shields.io/badge/Made%20with-Python-3776AB?logo=python&logoColor=white)](#)
[![Windows | macOS | Linux](https://img.shields.io/badge/Windows%20%7C%20macOS%20%7C%20Linux-supported-success)](#)
[![Works with diagrams.net](https://img.shields.io/badge/Works%20with-diagrams.net%20%2F%20Draw.io-brightgreen)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Validate](https://github.com/joelarbaiza/drawio-icon-libraries/actions/workflows/validate.yml/badge.svg)](https://github.com/joelarbaiza/drawio-icon-libraries/actions/workflows/validate.yml)

Colección de **librerías de iconos para Draw.io / diagrams.net** en formato `.xml` (**mxlibrary**): <!-- totals -->**30 librerías y 723 iconos vectoriales**<!-- /totals --> normalizados a **64×64**. Incluye un pipeline reproducible en Python para normalizar SVGs a 64×64 y **empaquetarlos** en librerías con `data:image/svg+xml;base64,...`.

> ⚠️ **Iconos y marcas**: los iconos y marcas pertenecen a sus respectivos titulares (p. ej., Microsoft). Este repo publica *librerías técnicas* y *scripts*; **no** transfiere derechos de uso. Consulta [docs/SOURCES.md](docs/SOURCES.md) para el origen y las condiciones de cada conjunto de iconos.

![Banner opcional](images/banner.png)

---

## 🧭 Índice

- [📚 Librerías incluidas](#librerias-incluidas)
- [🚀 Uso rápido en Draw.io/diagrams.net](#uso-rapido)
- [⬇️ Descarga](#descarga)
- [🛠️ Genera las librerías tú mismo](#generar)
- [⭐ Apóyame con una estrella](#estrella)
- [🤝 Contribuir](#contribuir)
- [👤 Autor](#autor)

---

<a id="librerias-incluidas"></a>

## 📚 Librerías incluidas

Archivos `.xml` listos para usar desde `/libraries`. **Abrir ↗** carga una librería directamente en diagrams.net (web), sin descargar nada.
> Sugerencia: **Ctrl/⌘ + clic** o **clic con la rueda** para abrirla en una pestaña nueva y no perder esta página.

<!-- BEGIN GENERATED: libraries -->
[![Abrir las 30 librerías en diagrams.net](https://img.shields.io/badge/diagrams.net-Abrir%20las%2030%20librer%C3%ADas-F08705?logo=diagramsdotnet&logoColor=white)](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20AI%20%2B%20Machine%20Learning%2FAzure%20AI%20%2B%20Machine%20Learning.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Analytics%2FAzure%20Analytics.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20App%20Services%2FAzure%20App%20Services.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Blockchain%2FAzure%20Blockchain.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Compute%2FAzure%20Compute.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Containers%2FAzure%20Containers.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Databases%2FAzure%20Databases.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20DevOps%2FAzure%20DevOps.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20General%2FAzure%20General.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Identity%2FAzure%20Identity.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Integration%2FAzure%20Integration.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Intune%2FAzure%20Intune.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20IoT%2FAzure%20IoT.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Management%20%2B%20Governance%2FAzure%20Management%20%2B%20Governance.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Migration%2FAzure%20Migration.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Monitor%2FAzure%20Monitor.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Networking%2FAzure%20Networking.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Security%2FAzure%20Security.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Storage%2FAzure%20Storage.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Web%2FAzure%20Web.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FDeveloping%2FDeveloping.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FDynamics%20365%2FDynamics%20365%20App%20Icons%2FDynamics%20365.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FDynamics%20365%2FDynamics%20365%20Mixed%20Reality%20Icons%2FDynamics%20365%20Mixed%20Reality.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FDynamics%20365%2FDynamics%20365%20Sub%20App%20Icons%2FDynamics%20365%20sub%20app%20icons.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FMicrosoft%20Entra%20ID%2FMicrosoft%20Entra%20ID.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FFabric%2FMicrosoft%20Fabric.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FOffice%20365%2FOffice%20365.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FOperating%20Systems%2FOperating%20Systems.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FPower%20Platform%2FPower%20Platform.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FProgramming%2FProgramming.xml)

| Librería | Iconos | Abrir en diagrams.net |
|---|---:|---|
| Azure AI + Machine Learning | 33 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20AI%20%2B%20Machine%20Learning%2FAzure%20AI%20%2B%20Machine%20Learning.xml) |
| Azure Analytics | 17 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Analytics%2FAzure%20Analytics.xml) |
| Azure App Services | 8 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20App%20Services%2FAzure%20App%20Services.xml) |
| Azure Blockchain | 6 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Blockchain%2FAzure%20Blockchain.xml) |
| Azure Compute | 40 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Compute%2FAzure%20Compute.xml) |
| Azure Containers | 7 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Containers%2FAzure%20Containers.xml) |
| Azure Databases | 27 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Databases%2FAzure%20Databases.xml) |
| Azure DevOps | 14 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20DevOps%2FAzure%20DevOps.xml) |
| Azure General | 96 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20General%2FAzure%20General.xml) |
| Azure Identity | 32 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Identity%2FAzure%20Identity.xml) |
| Azure Integration | 29 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Integration%2FAzure%20Integration.xml) |
| Azure Intune | 18 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Intune%2FAzure%20Intune.xml) |
| Azure IoT | 29 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20IoT%2FAzure%20IoT.xml) |
| Azure Management + Governance | 33 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Management%20%2B%20Governance%2FAzure%20Management%20%2B%20Governance.xml) |
| Azure Migration | 7 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Migration%2FAzure%20Migration.xml) |
| Azure Monitor | 11 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Monitor%2FAzure%20Monitor.xml) |
| Azure Networking | 51 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Networking%2FAzure%20Networking.xml) |
| Azure Security | 15 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Security%2FAzure%20Security.xml) |
| Azure Storage | 19 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Storage%2FAzure%20Storage.xml) |
| Azure Web | 19 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FAzure%2FAzure%20Web%2FAzure%20Web.xml) |
| Developing | 6 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FDeveloping%2FDeveloping.xml) |
| Dynamics 365 | 27 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FDynamics%20365%2FDynamics%20365%20App%20Icons%2FDynamics%20365.xml) |
| Dynamics 365 Mixed Reality | 7 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FDynamics%20365%2FDynamics%20365%20Mixed%20Reality%20Icons%2FDynamics%20365%20Mixed%20Reality.xml) |
| Dynamics 365 sub app icons | 4 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FDynamics%20365%2FDynamics%20365%20Sub%20App%20Icons%2FDynamics%20365%20sub%20app%20icons.xml) |
| Microsoft Entra ID | 7 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FMicrosoft%20Entra%20ID%2FMicrosoft%20Entra%20ID.xml) |
| Microsoft Fabric | 77 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FFabric%2FMicrosoft%20Fabric.xml) |
| Office 365 | 29 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FOffice%20365%2FOffice%20365.xml) |
| Operating Systems | 3 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FOperating%20Systems%2FOperating%20Systems.xml) |
| Power Platform | 9 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FPower%20Platform%2FPower%20Platform.xml) |
| Programming | 43 | [Abrir ↗](https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjoelarbaiza%2Fdrawio-icon-libraries%2Fmain%2Flibraries%2FProgramming%2FProgramming.xml) |
<!-- END GENERATED: libraries -->

Cada elemento lleva `w:64`, `h:64`, `aspect:"fixed"`, un `title` legible (p. ej. `Batch AI`, `Business Central`) y `data:image/svg+xml;base64,...`. Todos los iconos son vectoriales (sin imágenes embebidas), así que se ven nítidos a cualquier zoom.

> Algunos iconos de Azure aparecen en más de una librería de Azure, siguiendo las categorías de Microsoft.

---

<a id="uso-rapido"></a>

## 🚀 Uso rápido en Draw.io/diagrams.net

**Lo más rápido — diagrams.net en el navegador:** pulsa **Abrir ↗** junto a una librería en la
[tabla de arriba](#librerias-incluidas), o el botón **Abrir las … librerías**. diagrams.net se abre con la
librería ya en el panel izquierdo: no hay que descargar ni importar nada. Los enlaces cargan siempre la versión
más reciente de las librerías.
GitHub abre los enlaces en la misma pestaña; usa **Ctrl/⌘ + clic** o **clic con la rueda** para abrirlos en una nueva.

**Draw.io de escritorio (Windows) — instalador:**

1. [Descarga el ZIP](#descarga), descomprímelo y haz doble clic en **`install-drawio-desktop.bat`**.
   (O, en PowerShell y sin descargar nada: `irm https://raw.githubusercontent.com/joelarbaiza/drawio-icon-libraries/main/scripts/install-drawio-desktop.ps1 | iex`.)
2. **Solo la primera vez:** en Draw.io, importa cada librería que quieras con `Archivo → Abrir biblioteca desde →
   Archivo…`, eligiendo los `.xml` de la carpeta que abre el instalador. Draw.io las recuerda.
3. **Para actualizar:** vuelve a ejecutar el instalador. Reemplaza los archivos allí donde Draw.io ya los carga:
   verás los iconos nuevos sin duplicados y sin reimportar nada. También detecta las librerías que importaste a mano.

> Windows puede mostrar un aviso de SmartScreen con un script descargado: **Más información → Ejecutar de todas
> formas**. Draw.io de escritorio solo lee archivos locales que abres con su propio diálogo; por eso la primera
> importación es manual.

**macOS / Linux de escritorio o sin conexión:** [descarga el ZIP](#descarga), descomprímelo e importa cualquier
`.xml` de la carpeta `libraries` con `Archivo → Abrir biblioteca desde → Archivo…`.

Después arrastra los iconos desde el panel lateral al lienzo. Usa el buscador para encontrarlos por nombre.

---

<a id="descarga"></a>

## ⬇️ Descarga

[![Descargar librerías (ZIP)](https://img.shields.io/badge/Descargar-librer%C3%ADas%20ZIP-brightgreen)](https://github.com/joelarbaiza/drawio-icon-libraries/releases/latest/download/drawio-icon-libraries.zip)
[![Última versión](https://img.shields.io/github/v/release/joelarbaiza/drawio-icon-libraries?label=%C3%BAltima%20versi%C3%B3n&color=blue)](https://github.com/joelarbaiza/drawio-icon-libraries/releases/latest)

- **Descargar librerías ZIP** descarga directamente la última versión: todas las librerías `.xml` de `/libraries`, el instalador para Draw.io de escritorio en Windows, `LICENSE` y `SOURCES.md` (origen y licencia de los iconos).
- **última versión** muestra cuál es esa versión y abre sus [notas de la versión](https://github.com/joelarbaiza/drawio-icon-libraries/releases/latest) (qué cambió). Se actualiza sola en cada publicación.

---

<a id="generar"></a>

## 🛠️ Genera las librerías tú mismo

Solo hace falta para añadir o cambiar iconos; para *usar* las librerías basta con la descarga de arriba.

### Requisitos

| Para… | Necesitas |
|---|---|
| Regenerar las librerías `.xml`, cambiar títulos, validar | **Python 3.14+** (solo biblioteca estándar) |
| Añadir o cambiar iconos (normalizar SVG a 64×64) | Python 3.14+, **[Inkscape 1.x](https://inkscape.org)** y **Pillow** (`pip install -r requirements.txt`) |

Funciona en Windows, macOS y Linux; no hace falta WSL ni Jupyter.

### Uso

```bash
python scripts/build.py list -v                  # librerías, número de iconos y su carpeta source/
python scripts/build.py pack                     # regenera todos los .xml desde las carpetas 64/ (sin Inkscape)
python scripts/build.py all -l "Azure Web"       # normaliza + empaqueta una librería (requiere Inkscape)
python scripts/validate.py                       # las mismas comprobaciones que la CI
```

Cada librería se declara en [`libraries.json`](libraries.json) (carpeta de origen, archivo de salida, reglas de título).

### Estructura del repositorio

```
libraries/<…>.xml          librerías de Draw.io (generadas — no se editan a mano)
svg/…/<librería>/source/   SVG originales del proveedor (carpeta exacta: `build.py list -v`)
svg/…/<librería>/64/       SVG normalizados a 64×64 (generados, se commitean)
libraries.json             manifiesto: qué carpeta genera cada librería y cómo se titulan los iconos
scripts/                   build.py · validate.py · compare.py · package.py · iconlib/
docs/                      SOURCES.md (origen y condiciones) · ARCHITECTURE.md (cómo funciona)
```

---

<a id="estrella"></a>

## ⭐ Apóyame con una estrella

Si este proyecto te resulta útil, **¡regálale una estrella!** ⭐  
Eso ayuda a que más gente lo encuentre y me motiva a seguir mejorándolo.

[![Dame una estrella en GitHub](images/starred.png)](https://github.com/joelarbaiza/drawio-icon-libraries)

También puedes ver cuántas estrellas tiene ahora:
[![GitHub stars](https://img.shields.io/github/stars/joelarbaiza/drawio-icon-libraries?style=social)](https://github.com/joelarbaiza/drawio-icon-libraries/stargazers)

---

<a id="contribuir"></a>

## 🤝 Contribuir

¡Cualquier aporte es bienvenido! Puedes añadir iconos o librerías, mejorar los scripts o la documentación.

La guía completa —añadir iconos, crear una librería, reglas de título, comprobaciones de la CI y publicación de versiones— está en **[CONTRIBUTING.md](CONTRIBUTING.md)**. En resumen:

1. Crea una rama desde `main` (`feat/lib-<librería>` o `fix/<breve-descripcion>`).
2. Pon los SVG originales en la carpeta `source/` de la librería (ver `build.py list -v`) y ejecuta `python scripts/build.py all -l "<librería>"`.
3. Ejecuta `python scripts/validate.py` y revisa los iconos en Draw.io.
4. Commitea `source/`, `64/` y el `.xml` (y `libraries.json` si es una librería nueva), documenta el origen en `docs/SOURCES.md` y abre un Pull Request hacia `main`. La CI debe pasar en verde.

Consulta [CHANGELOG.md](CHANGELOG.md) para el historial de versiones y [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) para saber cómo funciona el pipeline.

---

<a id="autor"></a>

## 👤 Autor

Joel Arbaiza – [@LinkedIn](https://www.linkedin.com/in/joelarbaiza/)
