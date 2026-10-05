"""Lectura de ``libraries.json``: qué carpetas de SVG generan cada librería.

Estructura::

    {
      "defaults": {"padding": 3, "alpha_cutoff": 80, "render_px": 1024},
      "libraries": [
        {
          "name": "Azure Compute",
          "source": "svg/Azure/Azure Compute/SVG_18",       # SVG originales
          "normalized": "svg/Azure/Azure Compute/SVG_64",   # SVG 64×64 (commiteados)
          "output": "libraries/Azure/Azure Compute/Azure Compute.xml",
          "title_rules": [],                                # ver iconlib/titles.py
          "title_overrides": {"archivo-sin-svg": "Título"}  # opcional, gana a title_rules
        }
      ]
    }

Las rutas son relativas a la raíz del repositorio y siempre usan ``/``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, fields
from pathlib import Path

from .svg_normalize import NormalizeOptions
from .titles import check_rules

MANIFEST_NAME = "libraries.json"


@dataclass(frozen=True)
class Library:
    name: str
    source: Path
    normalized: Path
    output: Path
    title_rules: tuple[str, ...] = field(default_factory=tuple)
    # Título fijo por nombre de archivo (sin .svg); tiene prioridad sobre title_rules.
    title_overrides: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Manifest:
    root: Path
    options: NormalizeOptions
    libraries: tuple[Library, ...]

    def select(self, names: list[str] | None) -> list[Library]:
        if not names:
            return list(self.libraries)
        by_name = {lib.name.lower(): lib for lib in self.libraries}
        missing = [n for n in names if n.lower() not in by_name]
        if missing:
            raise ValueError(
                f"Librería(s) no encontrada(s) en {MANIFEST_NAME}: {', '.join(missing)}. "
                "Usa 'build.py list' para ver los nombres."
            )
        return [by_name[n.lower()] for n in names]


def load(root: Path) -> Manifest:
    path = root / MANIFEST_NAME
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FileNotFoundError(f"No existe {path}") from None
    except json.JSONDecodeError as e:
        raise ValueError(f"{path}: JSON inválido ({e})") from None

    if not isinstance(raw, dict):
        raise ValueError(f"{path}: se esperaba un objeto con 'defaults' y 'libraries'")

    defaults = raw.get("defaults", {})
    allowed = {f.name for f in fields(NormalizeOptions)}
    if not isinstance(defaults, dict):
        raise ValueError(f"{path}: 'defaults' debe ser un objeto")
    unknown = sorted(set(defaults) - allowed)
    if unknown:
        raise ValueError(f"{path}: clave(s) desconocida(s) en defaults: {', '.join(unknown)}. "
                         f"Válidas: {', '.join(sorted(allowed))}")
    bad = [k for k, v in defaults.items() if isinstance(v, bool) or not isinstance(v, (int, float))]
    if bad:
        raise ValueError(f"{path}: defaults.{bad[0]} debe ser numérico")
    options = NormalizeOptions(**defaults)

    entries = raw.get("libraries", [])
    if not isinstance(entries, list):
        raise ValueError(f"{path}: 'libraries' debe ser una lista")

    libraries = []
    seen: set[str] = set()
    for i, entry in enumerate(entries):
        missing = [k for k in ("name", "source", "normalized", "output") if k not in entry]
        if missing:
            raise ValueError(f"{path}: la entrada #{i} no tiene {', '.join(missing)}")
        name = entry["name"]
        if name.lower() in seen:
            raise ValueError(f"{path}: nombre de librería repetido: {name!r}")
        seen.add(name.lower())
        rules = entry.get("title_rules", [])
        if not isinstance(rules, list):
            raise ValueError(f"{path}: title_rules de {name!r} debe ser una lista, p. ej. [\"dash_to_space\"]")
        check_rules(rules)
        overrides = entry.get("title_overrides", {})
        if not isinstance(overrides, dict) or not all(
            isinstance(k, str) and isinstance(v, str) and v.strip() for k, v in overrides.items()
        ):
            raise ValueError(f"{path}: title_overrides de {name!r} debe ser un objeto {{\"archivo-sin-.svg\": \"Título\"}}")
        lib = Library(
            name=name,
            source=root / entry["source"],
            normalized=root / entry["normalized"],
            output=root / entry["output"],
            title_rules=tuple(rules),
            title_overrides=dict(overrides),
        )
        if lib.source.resolve() == lib.normalized.resolve():
            raise ValueError(f"{path}: {name!r} tiene source == normalized; normalize sobrescribiría los originales")
        libraries.append(lib)
    return Manifest(root=root, options=options, libraries=tuple(libraries))
