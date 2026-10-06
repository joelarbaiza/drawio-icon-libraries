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

Collection of **icon libraries for Draw.io / diagrams.net** in `.xml` (**mxlibrary**) format: **30 libraries, 723 vector icons** normalized to **64×64**. Includes a reproducible Python pipeline to normalize SVGs to 64×64 and **package** them into libraries using `data:image/svg+xml;base64,...`.

> ⚠️ **Icons and trademarks**: icons and trademarks belong to their respective owners (e.g., Microsoft). This repo publishes *technical libraries* and *scripts*; it does **not** transfer usage rights. See [docs/SOURCES.md](docs/SOURCES.md) for the origin and terms of each icon set.

![Optional banner](images/banner.png)

---

## 🧭 Table of contents

- [📚 Included libraries](#included-libraries)
- [🚀 Quick usage in Draw.io/diagrams.net](#quick-usage)
- [⬇️ Download](#download)
- [🛠️ Build the libraries yourself](#build)
- [⭐ Support with a star](#support-with-a-star)
- [🤝 Contributing](#contributing)
- [👤 Author](#author)

---

<a id="included-libraries"></a>

## 📚 Included libraries

`.xml` files ready to import from `/libraries`:

| Library | Icons | Library | Icons |
|---|---:|---|---:|
| Azure AI + Machine Learning | 33 | Azure Security | 15 |
| Azure Analytics | 17 | Azure Storage | 19 |
| Azure App Services | 8 | Azure Web | 19 |
| Azure Blockchain | 6 | Developing | 6 |
| Azure Compute | 40 | Dynamics 365 | 27 |
| Azure Containers | 7 | Dynamics 365 Mixed Reality | 7 |
| Azure Databases | 27 | Dynamics 365 sub app icons | 4 |
| Azure DevOps | 14 | Microsoft Entra ID | 7 |
| Azure General | 96 | Microsoft Fabric | 77 |
| Azure Identity | 32 | Office 365 | 29 |
| Azure Integration | 29 | Operating Systems | 3 |
| Azure Intune | 18 | Power Platform | 9 |
| Azure IoT | 29 | Programming | 43 |
| Azure Management + Governance | 33 | | |
| Azure Migration | 7 | | |
| Azure Monitor | 11 | | |
| Azure Networking | 51 | | |

Each entry uses `w:64`, `h:64`, `aspect:"fixed"`, a readable `title` (e.g. `Batch AI`, `Business Central`) and `data:image/svg+xml;base64,...`. All icons are vector (no embedded bitmaps), so they stay sharp at any zoom.

> Some Azure icons appear in more than one Azure library, following Microsoft's own categories.

---

<a id="quick-usage"></a>

## 🚀 Quick usage in Draw.io/diagrams.net

1. Open diagrams.net (or the Draw.io desktop app).
2. Go to `File → Open Library from → File…`.
3. Import any `.xml` from `/libraries`.
4. Drag icons from the side panel onto the canvas. Use the search box to find icons by name.

---

<a id="download"></a>

## ⬇️ Download

[![Download libraries (ZIP)](https://img.shields.io/badge/Download-libraries%20ZIP-brightgreen)](https://github.com/joelarbaiza/drawio-icon-libraries/releases/latest/download/drawio-icon-libraries.zip)
[![Latest release](https://img.shields.io/github/v/release/joelarbaiza/drawio-icon-libraries)](https://github.com/joelarbaiza/drawio-icon-libraries/releases/latest)

The ZIP contains every `.xml` library from `/libraries`, plus `LICENSE` and `SOURCES.md` (origin and license of the icons). It is built automatically for each release.

---

<a id="build"></a>

## 🛠️ Build the libraries yourself

You only need this to add or change icons; to *use* the libraries, the download above is enough.

### Requirements

| To… | You need |
|---|---|
| Rebuild the `.xml` libraries, change titles, validate | **Python 3.9+** (standard library only) |
| Add or change icons (normalize SVGs to 64×64) | Python 3.9+, **[Inkscape 1.x](https://inkscape.org)** and **Pillow** (`pip install -r requirements.txt`) |

Works on Windows, macOS and Linux; no WSL or Jupyter required.

### Usage

```bash
python scripts/build.py list -v                  # libraries, icon counts and their source/ folder
python scripts/build.py pack                     # rebuild every .xml from the 64/ folders (no Inkscape)
python scripts/build.py all -l "Azure Web"       # normalize + pack one library (needs Inkscape)
python scripts/validate.py                       # same checks as CI
```

Every library is declared in [`libraries.json`](libraries.json) (source folder, output file, title rules).

### Repository structure

```
libraries/<…>.xml          Draw.io libraries (generated — do not edit by hand)
svg/…/<library>/source/    original SVGs from the vendor (exact folder: `build.py list -v`)
svg/…/<library>/64/        SVGs normalized to 64×64 (generated, committed)
libraries.json             manifest: which folder builds which library, and how icons are titled
scripts/                   build.py · validate.py · compare.py · package.py · iconlib/
docs/                      SOURCES.md (icon origin and terms) · ARCHITECTURE.md (how it works)
```

---

<a id="support-with-a-star"></a>

## ⭐ Support with a star

If you find this project useful, please **give it a star!** ⭐  
It helps others find the project and motivates me to keep improving it.

[![Give me a star on GitHub](images/starred.png)](https://github.com/joelarbaiza/drawio-icon-libraries)

You can also see how many stars it has now:
[![GitHub stars](https://img.shields.io/github/stars/joelarbaiza/drawio-icon-libraries?style=social)](https://github.com/joelarbaiza/drawio-icon-libraries/stargazers)

---

<a id="contributing"></a>

## 🤝 Contributing

Contributions are welcome! Add new icons or libraries, improve the scripts or the documentation.

The full guide — adding icons, creating a library, title rules, checks run by CI, and releases — is in **[CONTRIBUTING.md](CONTRIBUTING.md)** (in Spanish). In short:

1. Create a branch from `main` (`feat/lib-<library>` or `fix/<short-description>`).
2. Put the original SVGs in the library's `source/` folder (see `build.py list -v`) and run `python scripts/build.py all -l "<library>"`.
3. Run `python scripts/validate.py` and check the icons in Draw.io.
4. Commit `source/`, `64/` and the `.xml` (plus `libraries.json` for a new library), document the origin in `docs/SOURCES.md`, and open a Pull Request to `main`. CI must pass.

See [CHANGELOG.md](CHANGELOG.md) for the release history and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for how the pipeline works.

---

<a id="author"></a>

## 👤 Author

Joel Arbaiza – [@LinkedIn](https://www.linkedin.com/in/joelarbaiza/)
