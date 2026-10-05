"""Compara librerías mxlibrary ítem a ítem: la copia de trabajo contra una referencia de git.

Sirve para demostrar que un cambio en el pipeline no altera los iconos.

Uso:
    python scripts/compare.py                 # libraries/ actual vs HEAD
    python scripts/compare.py --ref v0-legacy
    python scripts/compare.py --old A.xml --new B.xml

Por cada ítem (emparejados por posición) clasifica el SVG embebido en:
    idéntico      bytes iguales
    solo EOL      iguales tras convertir CRLF -> LF (cambio inocuo)
    DISTINTO      cualquier otra diferencia (regresión real)
y reporta aparte cambios de título y de número de ítems.

Sale con 1 si hay algún SVG DISTINTO, librerías que faltan/sobran o un número de
ítems diferente; los cambios de título solo fallan con --strict-titles.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from iconlib import mxlibrary  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


def git_show(root: Path, ref: str, path: str) -> str:
    r = subprocess.run(["git", "-C", str(root), "show", f"{ref}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise ValueError(f"git show {ref}:{path} falló: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout.decode("utf-8")


def git_ls(root: Path, ref: str) -> set[str]:
    # -z: rutas sin escapar (con core.quotePath, los nombres no ASCII saldrían entre comillas).
    r = subprocess.run(
        ["git", "-C", str(root), "ls-tree", "-r", "-z", "--name-only", ref, "--", "libraries"],
        capture_output=True,
    )
    if r.returncode != 0:
        raise ValueError(f"no se pudo leer la referencia {ref!r}: {r.stderr.decode('utf-8', 'replace').strip()}")
    return {p for p in r.stdout.decode("utf-8").split("\0") if p.endswith(".xml")}


def compare_items(name: str, old: list[dict], new: list[dict], counts: Counter, details: list[str]) -> None:
    if len(old) != len(new):
        counts["n_items"] += 1
        details.append(f"[n_items] {name}: {len(old)} -> {len(new)}")
    for i, (a, b) in enumerate(zip(old, new)):
        ta, tb = a.get("title"), b.get("title")
        if ta != tb:
            counts["titulo"] += 1
            details.append(f"[titulo] {name} #{i}: {ta!r} -> {tb!r}")
        for key in ("w", "h", "aspect"):
            if a.get(key) != b.get(key):
                counts["atributo"] += 1
                details.append(f"[atributo] {name} #{i} {key}: {a.get(key)!r} -> {b.get(key)!r}")
        sa, sb = mxlibrary.decode_svg(a), mxlibrary.decode_svg(b)
        if sa == sb:
            counts["identico"] += 1
        elif mxlibrary.canonical_svg_bytes(sa) == mxlibrary.canonical_svg_bytes(sb):
            counts["solo_eol"] += 1
        else:
            counts["distinto"] += 1
            details.append(f"[DISTINTO] {name} #{i} {tb!r}: {len(sa)} -> {len(sb)} bytes")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--root", type=Path, default=REPO_ROOT)
    p.add_argument("--ref", help="referencia de git a comparar (defecto: HEAD)")
    p.add_argument("--old", type=Path, help="comparar dos archivos sueltos: XML antiguo")
    p.add_argument("--new", type=Path, help="comparar dos archivos sueltos: XML nuevo")
    p.add_argument("--strict-titles", action="store_true", help="fallar también si cambia algún título")
    p.add_argument("-v", "--verbose", action="store_true", help="lista cada diferencia")
    args = p.parse_args()
    try:
        return run(args)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


def run(args) -> int:
    counts: Counter = Counter()
    details: list[str] = []
    root = args.root.resolve()

    if args.old or args.new:
        if not (args.old and args.new):
            raise ValueError("--old y --new van juntos")
        if args.ref:
            raise ValueError("--ref no se combina con --old/--new")
        compare_items(args.new.name, mxlibrary.read(args.old), mxlibrary.read(args.new), counts, details)
        n_libs = 1
    else:
        args.ref = args.ref or "HEAD"
        old_paths = git_ls(root, args.ref)
        new_paths = {p.relative_to(root).as_posix() for p in (root / "libraries").rglob("*.xml")}
        for path in sorted(old_paths - new_paths):
            counts["falta"] += 1
            details.append(f"[falta] {path} (existe en {args.ref})")
        for path in sorted(new_paths - old_paths):
            counts["sobra"] += 1
            details.append(f"[sobra] {path} (no existe en {args.ref})")
        common = sorted(old_paths & new_paths)
        for path in common:
            old = mxlibrary.loads(git_show(root, args.ref, path))
            new = mxlibrary.read(root / path)
            compare_items(path, old, new, counts, details)
        n_libs = len(common)

    if args.verbose:
        print("\n".join(details) + ("\n" if details else ""))

    print(f"Librerías comparadas: {n_libs}  (referencia: {'archivos' if args.old else args.ref})")
    for key, label in [("identico", "SVG idénticos"), ("solo_eol", "SVG solo EOL (CRLF->LF)"),
                       ("distinto", "SVG DISTINTOS"), ("titulo", "títulos cambiados"),
                       ("atributo", "w/h/aspect cambiados"), ("n_items", "nº de ítems distinto"),
                       ("falta", "librerías que faltan"), ("sobra", "librerías nuevas")]:
        print(f"  {label:<26} {counts[key]}")

    failed = counts["distinto"] or counts["atributo"] or counts["n_items"] or counts["falta"] or counts["sobra"] \
        or (args.strict_titles and counts["titulo"])
    print("\nFALLO" if failed else "\nOK: ningún icono cambió más allá de saltos de línea")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
