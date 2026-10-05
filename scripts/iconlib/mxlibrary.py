"""Lectura y escritura de librerías mxlibrary de Draw.io.

Formato: ``<mxlibrary>[{...}, ...]</mxlibrary>``, donde cada ítem es
``{"data": "data:image/svg+xml;base64,...", "w": 64, "h": 64, "title": "...", "aspect": "fixed"}``.

La salida es determinista en cualquier sistema operativo: los SVG se embeben
con saltos de línea LF (los CRLF que introduce un checkout en Windows se
convierten) y el XML se escribe en binario, sin salto de línea final.
"""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path
from typing import Iterable

from .titles import make_title

DATA_PREFIX = "data:image/svg+xml;base64,"
FALLBACK_SIZE = 64.0

_MXLIBRARY_RE = re.compile(r"^\s*<mxlibrary>(.*)</mxlibrary>\s*$", re.S)
_NUM_RE = re.compile(r"^\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)")


def canonical_svg_bytes(data: bytes) -> bytes:
    """Normaliza saltos de línea a LF para que el base64 no dependa del SO."""
    return data.replace(b"\r\n", b"\n")


def _float_from_unit(value: str | None) -> float | None:
    if not value:
        return None
    m = _NUM_RE.match(value)
    return float(m.group(1)) if m else None


def _viewbox_size(viewbox: str | None) -> tuple[float, float] | None:
    if not viewbox:
        return None
    parts = [p for p in re.split(r"[ ,]+", viewbox.strip()) if p]
    if len(parts) != 4:
        return None
    try:
        _, _, w, h = map(float, parts)
    except ValueError:
        return None
    return w, h


def intrinsic_size(svg: bytes) -> tuple[float, float]:
    """(w, h) a partir de viewBox o width/height de la cabecera; 64×64 si no se puede."""
    head = svg[:8000].decode("utf-8", errors="ignore")
    m_v = re.search(r'viewBox="([^"]+)"', head)
    if m_v:
        size = _viewbox_size(m_v.group(1))
        if size:
            return size
    m_w = re.search(r'width="([^"]+)"', head)
    m_h = re.search(r'height="([^"]+)"', head)
    w = _float_from_unit(m_w.group(1)) if m_w else None
    h = _float_from_unit(m_h.group(1)) if m_h else None
    if w and h:
        return w, h
    return FALLBACK_SIZE, FALLBACK_SIZE


def list_svgs(folder: Path) -> list[Path]:
    """SVG de la carpeta, ordenados por nombre sin distinguir mayúsculas."""
    return sorted(folder.glob("*.svg"), key=lambda p: p.name.lower())


def build_item(svg_path: Path, title_rules: Iterable[str] = ()) -> dict:
    data = canonical_svg_bytes(svg_path.read_bytes())
    w, h = intrinsic_size(data)
    return {
        "data": DATA_PREFIX + base64.b64encode(data).decode("ascii"),
        "w": int(round(w)),
        "h": int(round(h)),
        "title": make_title(svg_path.stem, title_rules),
        "aspect": "fixed",
    }


def build_items(folder: Path, title_rules: Iterable[str] = ()) -> list[dict]:
    title_rules = list(title_rules)
    return [build_item(p, title_rules) for p in list_svgs(folder)]


def dumps(items: list[dict]) -> str:
    return "<mxlibrary>" + json.dumps(items, ensure_ascii=False, separators=(",", ":")) + "</mxlibrary>"


def to_bytes(items: list[dict]) -> bytes:
    return dumps(items).encode("utf-8")


def write(items: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(to_bytes(items))


def loads(text: str) -> list[dict]:
    m = _MXLIBRARY_RE.match(text)
    if not m:
        raise ValueError("falta el envoltorio <mxlibrary>")
    items = json.loads(m.group(1))
    if not isinstance(items, list):
        raise ValueError("el contenido de <mxlibrary> no es una lista")
    return items


def read(path: Path) -> list[dict]:
    return loads(path.read_text(encoding="utf-8"))


def decode_svg(item: dict) -> bytes:
    data = item.get("data") or ""
    if not data.startswith(DATA_PREFIX):
        raise ValueError(f"data no empieza por {DATA_PREFIX}")
    return base64.b64decode(data[len(DATA_PREFIX):], validate=True)
