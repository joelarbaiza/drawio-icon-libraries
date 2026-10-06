"""Genera en README.md y README.es.md la tabla de librerías y los totales.

Uso:
    python scripts/readme.py           # actualiza los dos README
    python scripts/readme.py --check   # no escribe; falla si algún README está desactualizado (CI)

Partes generadas (entre marcadores; no las edites a mano):
    <!-- totals -->…<!-- /totals -->                          totales de la introducción
    <!-- BEGIN GENERATED: libraries -->…<!-- END GENERATED: libraries -->
        botón «abrir todas en diagrams.net» + tabla librería · iconos · enlace

Los enlaces abren app.diagrams.net con la librería ya cargada (parámetro `clibs`,
https://www.drawio.com/doc/faq/supported-url-parameters). Apuntan a los .xml de la
rama main en raw.githubusercontent.com, que permite CORS. La URL de cada librería se
codifica UNA sola vez: diagrams.net decodifica el parámetro y usa el nombre del archivo
como título de la librería; con doble codificación mostraría «Microsoft%20Fabric».

Solo usa la biblioteca estándar.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from iconlib import manifest as manifest_mod  # noqa: E402
from iconlib import mxlibrary  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_BASE = "https://raw.githubusercontent.com/joelarbaiza/drawio-icon-libraries/main/"
DRAWIO = "https://app.diagrams.net/?splash=0&clibs="

BLOCK_RE = re.compile(r"(<!-- BEGIN GENERATED: libraries -->\n).*?(\n<!-- END GENERATED: libraries -->)", re.S)
TOTALS_RE = re.compile(r"(<!-- totals -->).*?(<!-- /totals -->)", re.S)

TEXTS = {
    "README.md": {
        "totals": "**{libs} libraries, {icons} vector icons**",
        "badge": "Open all {libs} libraries in diagrams.net",
        "badge_img": "https://img.shields.io/badge/diagrams.net-Open%20all%20{libs}%20libraries-F08705?logo=diagramsdotnet&logoColor=white",
        "header": "| Library | Icons | Open in diagrams.net |",
        "open": "Open ↗",
    },
    "README.es.md": {
        "totals": "**{libs} librerías y {icons} iconos vectoriales**",
        "badge": "Abrir las {libs} librerías en diagrams.net",
        "badge_img": "https://img.shields.io/badge/diagrams.net-Abrir%20las%20{libs}%20librer%C3%ADas-F08705?logo=diagramsdotnet&logoColor=white",
        "header": "| Librería | Iconos | Abrir en diagrams.net |",
        "open": "Abrir ↗",
    },
}


def library_key(output: Path, root: Path) -> str:
    """Clave `U<url>` para clibs: URL raw del .xml codificada una sola vez."""
    raw_url = RAW_BASE + output.relative_to(root).as_posix()
    return "U" + urllib.parse.quote(raw_url, safe="")


def drawio_link(keys: list[str]) -> str:
    return DRAWIO + ";".join(keys)


def collect(root: Path) -> list[tuple[str, int, str]]:
    """(nombre, nº de iconos, clave clibs) por librería, ordenadas por nombre."""
    m = manifest_mod.load(root)
    rows = []
    for lib in m.libraries:
        if not lib.output.is_file():
            raise FileNotFoundError(f"No existe {lib.output}: ejecuta antes 'python scripts/build.py pack'")
        rows.append((lib.name, len(mxlibrary.read(lib.output)), library_key(lib.output, root)))
    return sorted(rows, key=lambda r: r[0].lower())


def render(rows: list[tuple[str, int, str]], t: dict) -> tuple[str, str]:
    libs, icons = len(rows), sum(r[1] for r in rows)
    totals = t["totals"].format(libs=libs, icons=icons)
    lines = [
        f"[![{t['badge'].format(libs=libs)}]({t['badge_img'].format(libs=libs)})]({drawio_link([r[2] for r in rows])})",
        "",
        t["header"],
        "|---|---:|---|",
    ]
    lines += [f"| {name} | {n} | [{t['open']}]({drawio_link([key])}) |" for name, n, key in rows]
    return totals, "\n".join(lines)


def update(text: str, totals: str, block: str, name: str) -> str:
    if not TOTALS_RE.search(text) or not BLOCK_RE.search(text):
        raise ValueError(f"{name}: faltan los marcadores <!-- totals --> o <!-- BEGIN GENERATED: libraries -->")
    text = TOTALS_RE.sub(lambda m: m.group(1) + totals + m.group(2), text)
    return BLOCK_RE.sub(lambda m: m.group(1) + block + m.group(2), text)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="raíz del repositorio")
    parser.add_argument("--check", action="store_true", help="no escribe; sale con 1 si algún README está desactualizado")
    args = parser.parse_args()

    root = args.root.resolve()
    try:
        rows = collect(root)
        stale = []
        for name, t in TEXTS.items():
            path = root / name
            old = path.read_text(encoding="utf-8")
            new = update(old, *render(rows, t), name)
            if new == old:
                continue
            stale.append(name)
            if not args.check:
                path.write_text(new, encoding="utf-8", newline="\n")
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    libs, icons = len(rows), sum(r[1] for r in rows)
    if args.check:
        if stale:
            print(f"Desactualizado(s): {', '.join(stale)}. Ejecuta: python scripts/readme.py")
            return 1
        print(f"OK: README al día ({libs} librerías, {icons} iconos)")
    else:
        print(f"{', '.join(stale) or 'Sin cambios'} · {libs} librerías, {icons} iconos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
