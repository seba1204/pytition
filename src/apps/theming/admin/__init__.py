"""Admin registrations for theming app."""

from __future__ import annotations

# Re-export ThemeAdmin to ensure Django auto-discovers it via apps.theming.admin
from .theme import ThemeAdmin

__all__ = ["ThemeAdmin"]
