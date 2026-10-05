"""Normalización de SVG a un lienzo fijo (64×64 por defecto), centrado y con margen.

Algoritmo (idéntico al de los notebooks originales):
    1. Inkscape rasteriza el SVG a PNG (``RENDER_PX`` de ancho, área de página).
    2. Con Pillow se calcula la caja del contenido visible: píxeles con
       alfa >= ``alpha_cutoff`` (ignora sombras suaves).
    3. Esa caja se traslada a unidades del viewBox original.
    4. Se envuelve el contenido en ``<g data-normalized="1">`` con
       ``translate(centro) scale(s) translate(-bbox)`` y se fija
       ``viewBox="0 0 64 64"``. El resultado sigue siendo 100 % vectorial.

Requisitos: Inkscape 1.x y Pillow. El binario de Inkscape se busca en este
orden: argumento ``inkscape``, variable de entorno ``INKSCAPE``, ``PATH`` y,
en Windows, la ruta de instalación por defecto.

Nota: el bbox depende del rasterizado de Inkscape, así que re-normalizar con
otra versión puede variar los decimales del ``transform``. No esperes
igualdad byte a byte entre versiones; compara con tolerancia numérica.
"""

from __future__ import annotations

import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)

_PLATFORM_DEFAULTS = {
    "win32": (
        r"C:\Program Files\Inkscape\bin\inkscape.com",  # envoltorio de consola
        r"C:\Program Files\Inkscape\bin\inkscape.exe",
        r"C:\Program Files (x86)\Inkscape\bin\inkscape.com",
        r"C:\Program Files (x86)\Inkscape\bin\inkscape.exe",
    ),
    "darwin": ("/Applications/Inkscape.app/Contents/MacOS/inkscape",),
}

# Número decimal con signo y exponente opcionales ("12", "-3.5", "1e-3", ".5").
_NUMBER = r"[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?"


@dataclass(frozen=True)
class NormalizeOptions:
    target_w: int = 64
    target_h: int = 64
    padding: float = 3          # margen interno en unidades del lienzo final
    alpha_cutoff: int = 80      # 0–255; ignora píxeles más transparentes
    render_px: int = 1024       # ancho del PNG de medición


class InkscapeNotFound(RuntimeError):
    pass


def _resolve(candidate: str) -> str | None:
    if Path(candidate).is_file():
        return str(Path(candidate))
    return shutil.which(candidate)


def find_inkscape(explicit: str | None = None) -> str:
    """Ruta del binario de Inkscape: --inkscape > $INKSCAPE > PATH > ruta por defecto del SO.

    Si se indica explícitamente (argumento o variable) y no existe, es un error:
    no se recurre en silencio a otra instalación.
    """
    for value, origin in ((explicit, "--inkscape"), (os.environ.get("INKSCAPE"), "INKSCAPE")):
        if value:
            found = _resolve(value)
            if not found:
                raise InkscapeNotFound(f"{origin}={value!r} no existe o no es ejecutable")
            return found
    found = shutil.which("inkscape")
    if found:
        return found
    for default in _PLATFORM_DEFAULTS.get(sys.platform, ()):
        if Path(default).is_file():
            return default
    raise InkscapeNotFound(
        "No se encontró Inkscape. Instálalo (https://inkscape.org) y asegúrate de que "
        "'inkscape' esté en el PATH, o indica la ruta con --inkscape o la variable INKSCAPE."
    )


def _parse_viewbox(vb: str) -> list[float]:
    nums = [float(x) for x in re.split(r"[ ,]+", vb.strip()) if x]
    if len(nums) != 4:
        raise ValueError(f"viewBox inválido: {vb!r}")
    return nums


def _float_from_unit(val: str | None) -> float:
    if val is None:
        raise ValueError("el SVG no tiene viewBox ni width/height")
    m = re.match(rf"\s*({_NUMBER})", str(val))
    if not m:
        raise ValueError(f"valor inválido: {val!r}")
    return float(m.group(1))


def _root_box(root: ET.Element) -> list[float]:
    vb = root.get("viewBox")
    if vb:
        return _parse_viewbox(vb)
    return [0.0, 0.0, _float_from_unit(root.get("width")), _float_from_unit(root.get("height"))]


def _is_normalized(svg_path: Path) -> bool:
    root = ET.parse(svg_path).getroot()
    return any(c.tag == f"{{{SVG_NS}}}g" and c.get("data-normalized") == "1" for c in root)


def _render_png(inkscape: str, svg_path: Path, png_path: Path, width_px: int) -> None:
    cmd = [
        inkscape,
        str(svg_path),
        "--export-type=png",
        f"--export-filename={png_path}",
        f"--export-width={width_px}",
        "--export-area-page",
    ]
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    # Inkscape puede salir con 0 sin haber exportado nada: comprobar también el archivo.
    if result.returncode != 0 or not png_path.is_file() or png_path.stat().st_size == 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(
            f"Inkscape no exportó {svg_path.name} (código {result.returncode})" + (f":\n{stderr}" if stderr else "")
        )


def measure_bbox(svg_path: Path, inkscape: str, opts: NormalizeOptions):
    """Caja visible (x, y, w, h) en unidades del viewBox, más el viewBox original.

    El PNG temporal se crea en el directorio de ``tempfile`` (respeta TMPDIR/TEMP);
    con Inkscape en snap/flatpak puede hacer falta apuntar TMPDIR a una carpeta del usuario.
    """
    from PIL import Image  # import diferido: solo `normalize` necesita Pillow

    minx, miny, vw, vh = _root_box(ET.parse(svg_path).getroot())

    with tempfile.TemporaryDirectory(prefix="bbox_") as tmpdir:
        tmp_png = Path(tmpdir) / "render.png"
        _render_png(inkscape, svg_path, tmp_png, opts.render_px)
        with Image.open(tmp_png) as img:
            img = img.convert("RGBA")
            out_w, out_h = img.size
            mask = img.split()[-1].point(lambda p: 255 if p >= opts.alpha_cutoff else 0, mode="L")
            bbox = mask.getbbox()

    bx_px, by_px, br_px, bb_px = bbox if bbox else (0, 0, out_w, out_h)
    bx = minx + (bx_px / out_w) * vw
    by = miny + (by_px / out_h) * vh
    bw = ((br_px - bx_px) / out_w) * vw
    bh = ((bb_px - by_px) / out_h) * vh
    return bx, by, bw, bh, (minx, miny, vw, vh)


def normalize_svg(src: Path, dst: Path, inkscape: str, opts: NormalizeOptions = NormalizeOptions()) -> None:
    """Escribe en ``dst`` la versión normalizada de ``src`` (``src`` no se modifica).

    Rechaza un ``src`` ya normalizado: su bbox se mediría en el espacio 64×64,
    pero el nuevo ``transform`` sustituiría al anterior y los hijos siguen en sus
    coordenadas originales, así que el icono quedaría mal escalado sin aviso.
    """
    if _is_normalized(src):
        raise ValueError(f"{src.name} ya está normalizado (tiene <g data-normalized=\"1\">); usa el SVG original")
    bx, by, bw, bh, _ = measure_bbox(src, inkscape, opts)

    inner_w = max(opts.target_w - 2 * opts.padding, 1)
    inner_h = max(opts.target_h - 2 * opts.padding, 1)
    s = min(inner_w / bw if bw else 1, inner_h / bh if bh else 1)
    left_off = (opts.target_w - s * bw) / 2
    top_off = (opts.target_h - s * bh) / 2

    tree = ET.parse(src)
    root = tree.getroot()
    children = list(root)
    defs = [c for c in children if c.tag == f"{{{SVG_NS}}}defs"]
    others = [c for c in children if c not in defs]

    for attr in ("width", "height"):
        root.attrib.pop(attr, None)
    root.set("viewBox", f"0 0 {opts.target_w} {opts.target_h}")
    root.set("width", str(opts.target_w))
    root.set("height", str(opts.target_h))
    root.set("preserveAspectRatio", "xMidYMid meet")

    # translate(centro) -> scale -> translate(-bbox)
    transform = (
        f"translate({left_off:.6f},{top_off:.6f}) "
        f"scale({s:.9f}) "
        f"translate({-bx:.6f},{-by:.6f})"
    )

    g = ET.Element(f"{{{SVG_NS}}}g", {"transform": transform, "data-normalized": "1"})
    for c in others:
        root.remove(c)
        g.append(c)
    root.append(g)

    # Escribir en binario: tree.write(ruta) abre en modo texto y en Windows
    # convertiría el salto de línea de la declaración XML en CRLF.
    buf = io.BytesIO()
    tree.write(buf, encoding="utf-8", xml_declaration=True)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(buf.getvalue())
