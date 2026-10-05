"""Genera las librerías de iconos de Draw.io a partir de los SVG del repositorio.

Flujo:  svg/<…>/source  --normalize-->  svg/<…>/64  --pack-->  libraries/<…>.xml

Uso:
    python scripts/build.py list
    python scripts/build.py pack                       # regenera las 30 librerías (solo stdlib)
    python scripts/build.py pack --check               # no escribe; falla si algún XML difiere
    python scripts/build.py normalize -l "Azure Web"   # requiere Inkscape + Pillow
    python scripts/build.py all -l "Azure Web"         # normalize + pack

    # Modo suelto, sin manifiesto:
    python scripts/build.py normalize --input DIR --output DIR
    python scripts/build.py pack --input DIR --output FILE.xml [--title-rule REGLA ...]

Las librerías y sus carpetas se declaran en libraries.json (raíz del repo).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parent))

from iconlib import manifest as manifest_mod  # noqa: E402
from iconlib import mxlibrary, svg_normalize  # noqa: E402
from iconlib.manifest import Library  # noqa: E402
from iconlib.titles import RULES, check_rules  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


class UsageError(Exception):
    pass


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


# ---------------------------------------------------------------- selección --

def resolve_targets(args) -> tuple[list[Library], svg_normalize.NormalizeOptions, Path]:
    """Librerías a procesar: del manifiesto (-l) o una ad hoc (--input/--output)."""
    root = args.root.resolve()
    title_rules = getattr(args, "title_rule", None) or []

    if args.input or args.output:
        if not (args.input and args.output):
            raise UsageError("--input y --output van juntos")
        if args.library:
            raise UsageError("usa --library o --input/--output, no ambos")
        if args.command == "all":
            raise UsageError("'all' solo funciona con el manifiesto; en modo suelto ejecuta normalize y luego pack")
        check_rules(title_rules)
        inp = args.input.resolve()
        out = args.output.resolve()
        if not inp.is_dir():
            raise UsageError(f"--input no es una carpeta: {args.input}")
        if args.command == "normalize":
            if inp == out:
                raise UsageError("--input y --output no pueden ser la misma carpeta (se sobrescribirían los originales)")
            normalized = out
        else:
            if out.is_dir() or out.suffix.lower() != ".xml":
                raise UsageError(f"--output debe ser un archivo .xml: {args.output}")
            normalized = inp
        lib = Library(name=out.stem, source=inp, normalized=normalized, output=out,
                      title_rules=tuple(title_rules))
        return [lib], svg_normalize.NormalizeOptions(), root

    if title_rules:
        raise UsageError("--title-rule solo aplica con --input/--output; en modo manifiesto usa title_rules en libraries.json")
    m = manifest_mod.load(root)
    return m.select(args.library), m.options, root


def apply_overrides(opts: svg_normalize.NormalizeOptions, args) -> svg_normalize.NormalizeOptions:
    changes = {k: getattr(args, k) for k in ("padding", "alpha_cutoff", "render_px") if getattr(args, k, None) is not None}
    return replace(opts, **changes) if changes else opts


def orphans(lib: Library) -> tuple[list[str], list[str]]:
    """(normalizados sin original, originales sin normalizar). Vacío si origen == normalizado."""
    if lib.source.resolve() == lib.normalized.resolve() or not lib.source.is_dir():
        return [], []
    src = {p.name for p in mxlibrary.list_svgs(lib.source)}
    norm = {p.name for p in mxlibrary.list_svgs(lib.normalized)} if lib.normalized.is_dir() else set()
    return sorted(norm - src), sorted(src - norm)


# ---------------------------------------------------------------- comandos --

def cmd_list(args) -> int:
    m = manifest_mod.load(args.root.resolve())
    for lib in m.libraries:
        n = len(mxlibrary.list_svgs(lib.normalized)) if lib.normalized.is_dir() else 0
        rules = ", ".join(lib.title_rules) or "—"
        print(f"{lib.name:<34} {n:>4} iconos  reglas: {rules}")
    print(f"\n{len(m.libraries)} librerías. Reglas de título disponibles: {', '.join(sorted(RULES))}")
    return 0


def do_normalize(libs: list[Library], opts, root: Path, args) -> int:
    if args.dry_run:
        inkscape = None
    else:
        inkscape = svg_normalize.find_inkscape(args.inkscape)
        print(f"Inkscape: {inkscape}")
    errors = 0
    for lib in libs:
        src = mxlibrary.list_svgs(lib.source) if lib.source.is_dir() else []
        if not src:
            print(f"[{lib.name}] sin SVG en {rel(lib.source, root)}", file=sys.stderr)
            errors += 1
            continue
        if args.dry_run:
            print(f"[{lib.name}] normalizaría {len(src)} SVG: {rel(lib.source, root)} -> {rel(lib.normalized, root)}")
        else:
            t0 = perf_counter()
            ok = 0
            for i, svg in enumerate(src, 1):
                try:
                    svg_normalize.normalize_svg(svg, lib.normalized / svg.name, inkscape, opts)
                except Exception as e:  # sigue con el resto y reporta al final
                    errors += 1
                    print(f"[{lib.name}] ERROR {svg.name}: {e}", file=sys.stderr)
                    continue
                ok += 1
                if args.verbose:
                    print(f"  [{i}/{len(src)}] {svg.name}")
            failed = f", {len(src) - ok} con error" if ok < len(src) else ""
            print(f"[{lib.name}] {ok}/{len(src)} SVG normalizados{failed} en {perf_counter() - t0:.1f}s "
                  f"-> {rel(lib.normalized, root)}")

        extra, _ = orphans(lib)
        if extra:
            if args.prune and not args.dry_run:
                for name in extra:
                    (lib.normalized / name).unlink()
                print(f"[{lib.name}] eliminados {len(extra)} SVG normalizados sin original: {', '.join(extra)}")
            else:
                verb = "se eliminarían" if args.prune else "sobran (usa --prune para eliminarlos)"
                print(f"[{lib.name}] {len(extra)} SVG normalizados sin original {verb}: {', '.join(extra)}",
                      file=sys.stderr)
                if not args.prune:
                    errors += 1
    return 1 if errors else 0


def do_pack(libs: list[Library], root: Path, args) -> int:
    errors = 0
    stale: list[str] = []
    for lib in libs:
        if not lib.normalized.is_dir() or not mxlibrary.list_svgs(lib.normalized):
            print(f"[{lib.name}] sin SVG en {rel(lib.normalized, root)}", file=sys.stderr)
            errors += 1
            continue
        extra, missing = orphans(lib)
        if extra or missing:
            if extra:
                print(f"[{lib.name}] SVG normalizados sin original (ejecuta normalize --prune): {', '.join(extra)}",
                      file=sys.stderr)
            if missing:
                print(f"[{lib.name}] originales sin normalizar (ejecuta normalize): {', '.join(missing)}",
                      file=sys.stderr)
            errors += 1
            continue

        try:
            items = mxlibrary.build_items(lib.normalized, lib.title_rules, lib.title_overrides)
        except ValueError as e:
            print(f"[{lib.name}] {e}", file=sys.stderr)
            errors += 1
            continue
        new = mxlibrary.to_bytes(items)
        target = rel(lib.output, root)

        if args.check:
            old = lib.output.read_bytes() if lib.output.is_file() else None
            if old != new:
                stale.append(target)
                print(f"[{lib.name}] DESACTUALIZADO: {target}")
            elif args.verbose:
                print(f"[{lib.name}] ok")
            continue
        if args.dry_run:
            print(f"[{lib.name}] escribiría {len(items)} iconos -> {target}")
            continue
        changed = not lib.output.is_file() or lib.output.read_bytes() != new
        mxlibrary.write(items, lib.output)
        if changed or args.verbose:
            print(f"[{lib.name}] {len(items)} iconos -> {target}{'' if changed else ' (sin cambios)'}")

    if args.check:
        if stale:
            print(f"\n{len(stale)} librería(s) no coinciden con sus SVG. Ejecuta: python scripts/build.py pack")
        if errors:
            print(f"\n{errors} librería(s) con errores (ver arriba)")
        if not stale and not errors:
            print(f"OK: {len(libs)} librería(s) al día")
    return 1 if errors or stale else 0


def cmd_normalize(args) -> int:
    libs, opts, root = resolve_targets(args)
    return do_normalize(libs, apply_overrides(opts, args), root, args)


def cmd_pack(args) -> int:
    libs, _, root = resolve_targets(args)
    return do_pack(libs, root, args)


def cmd_all(args) -> int:
    if args.check:
        raise UsageError("'all --check' no tiene sentido (normalize escribiría antes de comprobar); usa 'pack --check'")
    libs, opts, root = resolve_targets(args)
    rc = do_normalize(libs, apply_overrides(opts, args), root, args)
    if rc:
        print("normalize falló; no se empaqueta", file=sys.stderr)
        return rc
    return do_pack(libs, root, args)


# --------------------------------------------------------------------- CLI --

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="build.py",
        description="Genera librerías mxlibrary de Draw.io a partir de SVG.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Uso:", 1)[1],
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="raíz del repositorio (por defecto, la del script)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="muestra las librerías del manifiesto").set_defaults(func=cmd_list)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("-l", "--library", action="append", metavar="NOMBRE",
                        help="procesa solo esta librería del manifiesto (repetible; por defecto, todas)")
    common.add_argument("--input", type=Path, help="modo suelto: carpeta de SVG de entrada")
    common.add_argument("--output", type=Path, help="modo suelto: carpeta (normalize) o .xml (pack) de salida")
    common.add_argument("--dry-run", action="store_true", help="muestra qué haría sin escribir nada")
    common.add_argument("-v", "--verbose", action="store_true")

    norm = argparse.ArgumentParser(add_help=False)
    norm.add_argument("--inkscape", metavar="RUTA", help="binario de Inkscape (por defecto: $INKSCAPE o el PATH)")
    norm.add_argument("--padding", type=float, help="margen interno en px del lienzo final (defecto: 3)")
    norm.add_argument("--alpha-cutoff", type=int, help="umbral de alfa 0–255 para medir el contenido (defecto: 80)")
    norm.add_argument("--render-px", type=int, help="ancho del PNG de medición (defecto: 1024)")
    norm.add_argument("--prune", action="store_true",
                      help="elimina SVG normalizados cuyo original ya no existe")

    pack = argparse.ArgumentParser(add_help=False)
    pack.add_argument("--title-rule", action="append", metavar="REGLA",
                      help=f"modo suelto: regla de título (repetible): {', '.join(sorted(RULES))}")
    pack.add_argument("--check", action="store_true",
                      help="no escribe; sale con 1 si algún XML no coincide con sus SVG (para CI)")

    p_norm = sub.add_parser("normalize", parents=[common, norm],
                            help="SVG originales -> SVG 64×64 (Inkscape + Pillow)")
    p_norm.set_defaults(func=cmd_normalize, title_rule=None, check=False)
    p_pack = sub.add_parser("pack", parents=[common, pack],
                            help="SVG 64×64 -> librería .xml (solo stdlib)")
    p_pack.set_defaults(func=cmd_pack)
    p_all = sub.add_parser("all", parents=[common, norm, pack], help="normalize + pack")
    p_all.set_defaults(func=cmd_all)
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (UsageError, ValueError, OSError, svg_normalize.InkscapeNotFound) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
