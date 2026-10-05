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


RULES: dict[str, Rule] = {
    # "00028-icon-service-Batch-AI" -> "Batch-AI"
    "strip_azure_prefix": _sub(r"^\d+-icon-service-", ""),
    # "Batch-AI" -> "Batch AI"
    "dash_to_space": lambda title: title.replace("-", " "),
    # "BusinessCentral scalable" -> "BusinessCentral"
    "strip_scalable": _sub(r" scalable$", "", re.I),
    # "add pipeline 48 non-item" / "apps 48 item" / "copilot 48 color" -> "add pipeline" / ...
    "strip_size_suffix": _sub(r" 48( \S+)?$", ""),
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
