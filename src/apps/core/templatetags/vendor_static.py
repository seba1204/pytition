"""Django template tag to reference versioned vendor static files."""

from __future__ import annotations

import tomllib
from functools import lru_cache
from pathlib import Path

from django import template
from django.templatetags.static import static

register = template.Library()


@lru_cache
def _load_versions() -> dict[str, str]:
    """Load vendor versions from pyproject.toml."""
    pyproject = Path(__file__).resolve().parents[4] / "pyproject.toml"
    with Path.open(pyproject, "rb") as f:
        cfg = tomllib.load(f)
    vendors = cfg.get("tool", {}).get("pytition", {}).get("vendors", {})
    if not isinstance(vendors, dict):
        return {}
    # Ensure all keys and values are strings
    return {str(k): str(v) for k, v in vendors.items()}


@register.simple_tag
def vendor_static(vendor: str, path: str) -> str:
    """Builds a static path to a versioned vendor."""
    versions = _load_versions()
    version = versions.get(vendor)
    if not version:
        raise template.TemplateSyntaxError(f"Unknown version for '{vendor}'")
    return static(f"vendor/{vendor}-{version}/{path}")
