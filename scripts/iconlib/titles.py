"""Reglas para derivar el título visible (``title``) de cada icono.

El título base sale del nombre de archivo sin extensión, con ``_`` → espacio
(comportamiento histórico de los notebooks). Después se aplican, en orden,
las reglas declaradas para la librería en ``libraries.json``.
"""

from __future__ import annotations

import re
from typing import Callable, Iterable

Rule = Callable[[str], str]


def _sub(pattern: str, repl: str, flags: int = 0) -> Rule:
    regex = re.compile(pattern, flags)
    return lambda title: regex.sub(repl, title)


def _fabric_suffix(title: str) -> str:
    # El paquete de Fabric distingue variantes del mismo concepto ("data warehouse 48 color"
    # y "data warehouse 48 item" son iconos distintos): se conserva la variante salvo "item".
    m = re.match(r"^(.*) 48(?: (\S+))?$", title)
    if not m:
        return title
    name, variant = m.groups()
    return name if variant in (None, "item") else f"{name} ({variant})"


RULES: dict[str, Rule] = {
    # "00028-icon-service-Batch-AI" -> "Batch-AI"
    "strip_azure_prefix": _sub(r"^\d+-icon-service-", ""),
    # "Batch-AI" -> "Batch AI"
    "dash_to_space": lambda title: title.replace("-", " "),
    # "BusinessCentral scalable" / "IntelligentOrderManagement scalable (1)" -> sin sufijo
    "strip_scalable": _sub(r" scalable(?: \(\d+\))?$", "", re.I),
    # "BusinessCentral" -> "Business Central", "AIBuilder" -> "AI Builder", "Dynamics365" -> "Dynamics 365"
    "split_camel_case": _sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|(?<=[A-Za-z])(?=\d)", " "),
    # "lakehouse 48 item" -> "lakehouse", "data warehouse 48 color" -> "data warehouse (color)"
    "fabric_suffix": _fabric_suffix,
    # "Microsoft Entra ID color icon" -> "Microsoft Entra ID"
    "strip_color_icon": _sub(r" color icon$", "", re.I),
}


def base_title(stem: str) -> str:
    return stem.replace("_", " ")


def check_rules(rules: Iterable[str]) -> None:
    unknown = [name for name in rules if name not in RULES]
    if unknown:
        raise ValueError(
            f"Regla(s) de título desconocida(s): {', '.join(unknown)}. "
            f"Disponibles: {', '.join(sorted(RULES))}"
        )


def apply_rules(title: str, rules: Iterable[str]) -> str:
    rules = list(rules)
    check_rules(rules)
    if not rules:
        return title
    for name in rules:
        title = RULES[name](title)
    # Las reglas pueden dejar espacios dobles o en los extremos.
    return " ".join(title.split())


def make_title(stem: str, rules: Iterable[str] = ()) -> str:
    return apply_rules(base_title(stem), rules)
