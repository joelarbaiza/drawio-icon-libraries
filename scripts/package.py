"""Empaqueta las librerías en un ZIP listo para publicar en una GitHub Release.

Uso:
    python scripts/package.py                    # -> dist/drawio-icon-libraries.zip
    python scripts/package.py --output OTRO.zip

Contenido del ZIP (dentro de una carpeta drawio-icon-libraries/):
    libraries/**/*.xml   las librerías de Draw.io
    LICENSE              licencia de los scripts
    SOURCES.md           origen y licencia de los iconos (docs/SOURCES.md)
    install-drawio-desktop.bat / .ps1   instalador para Draw.io de escritorio (Windows)

El ZIP es reproducible en una misma plataforma (orden y fechas fijos): mismas
entradas -> mismos bytes. Entre plataformas el contenido es el mismo, pero los
bytes comprimidos pueden variar con la implementación de zlib (p. ej. zlib-ng en
Python para Windows). La release oficial se genera siempre en Linux (release.yml).
Solo usa la biblioteca estándar.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ZIP_NAME = "drawio-icon-libraries.zip"
TOP = "drawio-icon-libraries"
FIXED_DATE = (2020, 1, 1, 0, 0, 0)


def files_to_pack(root: Path) -> list[tuple[Path, str]]:
    """(ruta en disco, ruta dentro del ZIP), ordenados."""
    libs = sorted((root / "libraries").rglob("*.xml"), key=lambda p: p.relative_to(root).as_posix())
    if not libs:
        raise FileNotFoundError(f"No hay librerías en {root / 'libraries'}")
    entries = [(p, f"{TOP}/{p.relative_to(root).as_posix()}") for p in libs]
    extras = (
        (root / "LICENSE", "LICENSE"),
        (root / "docs" / "SOURCES.md", "SOURCES.md"),
        # Instalador para Draw.io de escritorio (Windows): doble clic en el .bat.
        (root / "scripts" / "install-drawio-desktop.bat", "install-drawio-desktop.bat"),
        (root / "scripts" / "install-drawio-desktop.ps1", "install-drawio-desktop.ps1"),
    )
    for src, arc in extras:
        if not src.is_file():
            raise FileNotFoundError(f"Falta {src}")
        entries.append((src, f"{TOP}/{arc}"))
    return entries


def build_zip(root: Path, output: Path) -> int:
    entries = files_to_pack(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for src, arc in entries:
            info = zipfile.ZipInfo(arc, date_time=FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, src.read_bytes())
    return len(entries)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="raíz del repositorio")
    parser.add_argument("--output", type=Path, help=f"ZIP de salida (defecto: dist/{ZIP_NAME})")
    args = parser.parse_args()

    root = args.root.resolve()
    output = (args.output or root / "dist" / ZIP_NAME).resolve()
    try:
        n = build_zip(root, output)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(f"{output} · {n} archivos · {output.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
