from __future__ import annotations

import tomllib
from functools import lru_cache
from pathlib import Path

from django import template
from django.templatetags.static import static

register = template.Library()


@lru_cache
def _load_versions() -> dict[str, str]:
    pyproject = Path(__file__).resolve().parents[4] / "pyproject.toml"
    with open(pyproject, "rb") as f:
        cfg = tomllib.load(f)
    return cfg.get("tool", {}).get("pytition", {}).get("vendors", {})


@register.simple_tag
def vendor_static(vendor: str, path: str) -> str:
    """Construit un chemin static vers un vendor versionné."""
    versions = _load_versions()
    version = versions.get(vendor)
    if not version:
        raise template.TemplateSyntaxError(f"Version inconnue pour '{vendor}'")
    return static(f"vendor/{vendor}-{version}/{path}")
