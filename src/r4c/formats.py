from __future__ import annotations

import re
from typing import Mapping


LIST_FORMATS = ("table", "turtle")

_TURTLE_PREFIX_RE = re.compile(r"^\s*@prefix\s+([^:\s]*):\s*<([^>]*)>\s*\.\s*$", re.I)
_TURTLE_11_PREFIX_RE = re.compile(r"^\s*prefix\s+([^:\s]*):\s*<([^>]*)>\s*$", re.I)


def format_namespaces(namespaces: Mapping[str, str]) -> str:
    ordered = dict(sorted(namespaces.items()))
    return "".join(
        f"PREFIX {_prefix_label(prefix)}: <{namespace}>\n"
        for prefix, namespace in ordered.items()
    )


def parse_namespaces(text: str) -> dict[str, str]:
    namespaces: dict[str, str] = {}
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = _TURTLE_11_PREFIX_RE.match(line) or _TURTLE_PREFIX_RE.match(line)
        if not match:
            raise ValueError(f"Line {line_number} is not a Turtle prefix declaration")
        namespaces[match.group(1)] = match.group(2)
    return namespaces


def _prefix_label(prefix: str) -> str:
    return prefix
