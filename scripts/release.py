"""Prepara una versión: calcula el número, actualiza CHANGELOG.md y pyproject.toml.

Lo usa el workflow «Publicar versión» (.github/workflows/publish.yml), pero también
se puede ejecutar en local para ver qué haría.

Uso:
    python scripts/release.py next --bump minor        # imprime la versión siguiente (1.1.0)
    python scripts/release.py prepare --version 1.1.0  # CHANGELOG + pyproject.toml
    python scripts/release.py notes --version 1.1.0    # imprime la sección de esa versión

`prepare` convierte la sección «## [Sin publicar]» del CHANGELOG en
«## [1.1.0] - AAAA-MM-DD», deja encima una sección «Sin publicar» vacía para la
siguiente versión y añade el enlace a la release. Falla si «Sin publicar» está
vacía: no se publica una versión sin cambios documentados.

Solo usa la biblioteca estándar.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
UNRELEASED = "## [Sin publicar]"
REPO_URL = "https://github.com/joelarbaiza/drawio-icon-libraries"
VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


class ReleaseError(Exception):
    pass


def parse_version(text: str) -> tuple[int, int, int]:
    m = VERSION_RE.match(text.strip())
    if not m:
        raise ReleaseError(f"versión inválida: {text!r} (se espera X.Y.Z)")
    return tuple(int(x) for x in m.groups())  # type: ignore[return-value]


def latest_tag(root: Path) -> tuple[int, int, int]:
    r = subprocess.run(["git", "-C", str(root), "tag", "--list", "v*"], capture_output=True, text=True)
    if r.returncode != 0:
        raise ReleaseError(f"no se pudieron leer los tags: {r.stderr.strip()}")
    versions = [parse_version(t) for t in r.stdout.split() if VERSION_RE.match(t)]
    if not versions:
        raise ReleaseError("no hay ningún tag vX.Y.Z; crea el primero a mano")
    return max(versions)


def bump(version: tuple[int, int, int], part: str) -> str:
    major, minor, patch = version
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ReleaseError(f"tipo de incremento desconocido: {part}")


def _section_bounds(text: str, heading: str) -> tuple[int, int]:
    """(inicio del contenido, fin) de la sección que empieza en `heading`."""
    start = text.find(heading + "\n")
    if start < 0:
        raise ReleaseError(f"no se encontró «{heading}» en CHANGELOG.md")
    body = start + len(heading) + 1
    nxt = re.search(r"^## \[", text[body:], re.M)
    links = re.search(r"^\[[^\]]+\]: ", text[body:], re.M)
    ends = [m.start() + body for m in (nxt, links) if m]
    return body, min(ends) if ends else len(text)


def prepare_changelog(text: str, version: str, date: str) -> str:
    if f"## [{version}]" in text:
        raise ReleaseError(f"la versión {version} ya está en CHANGELOG.md")
    body, end = _section_bounds(text, UNRELEASED)
    if not text[body:end].strip():
        raise ReleaseError("la sección «Sin publicar» del CHANGELOG está vacía: documenta los cambios antes de publicar")
    text = text.replace(UNRELEASED + "\n", f"{UNRELEASED}\n\n## [{version}] - {date}\n", 1)
    link = f"[{version}]: {REPO_URL}/releases/tag/v{version}\n"
    m = re.search(r"^\[[^\]]+\]: ", text, re.M)
    if m:                                   # enlaces de referencia al final: el nuevo primero
        text = text[: m.start()] + link + text[m.start():]
    else:
        text = text.rstrip("\n") + "\n\n" + link
    return text


def release_notes(text: str, version: str) -> str:
    body, end = _section_bounds(text, f"## [{version}]" + _date_suffix(text, version))
    return text[body:end].strip() + "\n"


def _date_suffix(text: str, version: str) -> str:
    m = re.search(rf"^## \[{re.escape(version)}\]( - [^\n]*)?$", text, re.M)
    if not m:
        raise ReleaseError(f"no se encontró la versión {version} en CHANGELOG.md")
    return m.group(1) or ""


def prepare_pyproject(text: str, version: str) -> str:
    new, n = re.subn(r'(?m)^version = "[^"]*"$', f'version = "{version}"', text, count=1)
    if n != 1:
        raise ReleaseError("no se encontró la línea version = \"…\" en pyproject.toml")
    return new


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="raíz del repositorio")
    sub = parser.add_subparsers(dest="command", required=True)
    p_next = sub.add_parser("next", help="imprime la versión siguiente según el último tag vX.Y.Z")
    p_next.add_argument("--bump", choices=["patch", "minor", "major"], required=True)
    p_prep = sub.add_parser("prepare", help="actualiza CHANGELOG.md y pyproject.toml")
    p_prep.add_argument("--version", required=True)
    p_prep.add_argument("--date", default=dt.date.today().isoformat(), help="AAAA-MM-DD (defecto: hoy)")
    p_prep.add_argument("--dry-run", action="store_true", help="muestra el CHANGELOG resultante sin escribir")
    p_notes = sub.add_parser("notes", help="imprime las notas de una versión del CHANGELOG")
    p_notes.add_argument("--version", required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    changelog = root / "CHANGELOG.md"
    pyproject = root / "pyproject.toml"
    try:
        if args.command == "next":
            print(bump(latest_tag(root), args.bump))
        elif args.command == "prepare":
            version = ".".join(map(str, parse_version(args.version)))
            dt.date.fromisoformat(args.date)
            new_changelog = prepare_changelog(changelog.read_text(encoding="utf-8"), version, args.date)
            new_pyproject = prepare_pyproject(pyproject.read_text(encoding="utf-8"), version)
            if args.dry_run:
                print(new_changelog)
            else:
                changelog.write_text(new_changelog, encoding="utf-8", newline="\n")
                pyproject.write_text(new_pyproject, encoding="utf-8", newline="\n")
                print(f"CHANGELOG.md y pyproject.toml preparados para {version} ({args.date})")
        elif args.command == "notes":
            version = ".".join(map(str, parse_version(args.version)))
            sys.stdout.write(release_notes(changelog.read_text(encoding="utf-8"), version))
    except (ReleaseError, ValueError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
