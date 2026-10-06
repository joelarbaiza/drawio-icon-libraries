"""Valida las librerías mxlibrary de Draw.io en libraries/.

Uso:
    python scripts/validate.py [--root DIR] [--verbose]

Comprobaciones por librería (*.xml):
    - Envoltorio <mxlibrary> con JSON válido (lista de ítems).
    - Cada ítem: w=64, h=64, aspect="fixed", data:image/svg+xml;base64,...
    - El SVG decodificado es XML bien formado.
    - Título no vacío y "limpio" (sin prefijos/sufijos heredados del nombre de archivo).
    - Sin raster embebido (<image>) salvo los de RASTER_ALLOWLIST.
    - Sin títulos duplicados dentro de la librería.

Sale con código 1 si hay algún error; 0 si todo pasa.
Solo usa la biblioteca estándar de Python (3.9+).
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import re
import sys
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

TARGET_SIZE = 64
DATA_PREFIX = "data:image/svg+xml;base64,"

# Patrones de título "crudo" (heredado del nombre de archivo) -> motivo.
RAW_TITLE_PATTERNS = [
    (re.compile(r"^\d+-icon-service-"), "prefijo Azure '<n>-icon-service-'"),
    (re.compile(r" scalable(?: \(\d+\))?$", re.I), "sufijo ' scalable'"),
    (re.compile(r" color icon$", re.I), "sufijo ' color icon'"),
    (re.compile(r" 48( \S+)?$"), "sufijo de tamaño ' 48 ...'"),
    (re.compile(r"\.svg$", re.I), "extensión '.svg'"),
]

# Iconos autorizados a embeber raster (<image>), por librería y título, con su
# justificación en docs/SOURCES.md. Vacía desde la etapa 4: todos son vectoriales.
RASTER_ALLOWLIST: dict[str, set[str]] = {}

MXLIBRARY_RE = re.compile(r"^\s*<mxlibrary>(.*)</mxlibrary>\s*$", re.S)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.counts: Counter[str] = Counter()

    def error(self, kind: str, msg: str) -> None:
        self.counts[kind] += 1
        self.errors.append(f"[{kind}] {msg}")


def validate_library(path: Path, root: Path, report: Report) -> int:
    """Valida un .xml y devuelve el número de ítems leídos."""
    rel = path.relative_to(root).as_posix()
    lib = path.stem
    raw = path.read_text(encoding="utf-8")

    m = MXLIBRARY_RE.match(raw)
    if not m:
        report.error("formato", f"{rel}: falta el envoltorio <mxlibrary>")
        return 0
    try:
        items = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        report.error("formato", f"{rel}: JSON inválido ({e})")
        return 0
    if not isinstance(items, list):
        report.error("formato", f"{rel}: el contenido no es una lista")
        return 0

    allowed_raster = RASTER_ALLOWLIST.get(lib, set())
    titles: Counter[str] = Counter()

    for idx, item in enumerate(items):
        title = str(item.get("title") or "")
        where = f"{rel} #{idx} '{title}'"
        titles[title] += 1

        if item.get("w") != TARGET_SIZE or item.get("h") != TARGET_SIZE:
            report.error("tamaño", f"{where}: w/h = {item.get('w')}x{item.get('h')}")
        if item.get("aspect") != "fixed":
            report.error("tamaño", f"{where}: aspect = {item.get('aspect')!r}")

        if not title.strip():
            report.error("titulo", f"{where}: título vacío")
        for pattern, reason in RAW_TITLE_PATTERNS:
            if pattern.search(title):
                report.error("titulo", f"{where}: {reason}")
                break

        data = item.get("data") or ""
        if not data.startswith(DATA_PREFIX):
            report.error("svg", f"{where}: data no es {DATA_PREFIX}...")
            continue
        try:
            svg = base64.b64decode(data[len(DATA_PREFIX):], validate=True)
            ET.fromstring(svg)
        except (binascii.Error, ET.ParseError) as e:
            report.error("svg", f"{where}: SVG ilegible ({e})")
            continue

        if b"<image" in svg:
            if title in allowed_raster:
                report.counts["raster permitido"] += 1
            else:
                report.error("raster", f"{where}: embebe <image> ({len(svg) // 1024} KB)")

    for title, n in titles.items():
        if n > 1 and title:
            report.error("duplicado", f"{rel}: título '{title}' repetido {n} veces")

    return len(items)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="raíz del repositorio (por defecto, la del script)")
    parser.add_argument("--verbose", "-v", action="store_true", help="lista cada error")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parser.parse_args()

    root = args.root.resolve()
    libraries = sorted((root / "libraries").rglob("*.xml"))
    if not libraries:
        print(f"No se encontraron librerías en {root / 'libraries'}")
        return 1

    report = Report()
    total = sum(validate_library(p, root, report) for p in libraries)

    if args.verbose:
        for line in report.errors:
            print(line)
        print()

    print(f"Librerías: {len(libraries)}  ·  Ítems: {total}")
    for kind in ("formato", "tamaño", "svg", "titulo", "raster", "duplicado", "raster permitido"):
        print(f"  {kind:<17} {report.counts[kind]}")

    if report.errors:
        print(f"\nFALLO: {len(report.errors)} errores (usa --verbose para el detalle)")
        return 1
    print("\nOK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
