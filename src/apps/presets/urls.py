"""
Organizations URL declarations built from the PresetRoutes enum.

This module maps each :class:`PresetRoutes` member to an actual Django URL pattern
and view, validates the bijection, and exposes `urlpatterns`.
"""

from __future__ import annotations

from django.urls import URLPattern

from apps.core.routes import Route, build_urlpatterns, validate_bijection
from apps.presets import views as PrV
from apps.presets.routes import PresetRoutes

app_name = "presets"

ID = "<int:preset_id>"

# --------------------------------------------------------------------------- #
# One-to-one mapping: every PresetRoutes must appear exactly once
# --------------------------------------------------------------------------- #

ROUTES: dict[PresetRoutes, Route] = {
    PresetRoutes.NEW: Route("new", PrV.new),
    PresetRoutes.EDIT: Route(f"{ID}/edit", PrV.edit),
    PresetRoutes.TOGGLE_FAV: Route(f"{ID}/fav", PrV.toggle_fav),
    PresetRoutes.DELETE: Route(f"{ID}/delete", PrV.delete),
}

# Fail fast at import time (CI-friendly)
validate_bijection(PresetRoutes, ROUTES)

# Short-named patterns; the namespace is supplied by include(..., namespace=NAMESPACE)
urlpatterns: list[URLPattern] = build_urlpatterns(ROUTES)
