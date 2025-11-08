"""Caching services for theming CSS payloads."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.cache import cache

if TYPE_CHECKING:
    from apps.theming.models import Theme

CACHE_TTL_SECONDS = 24 * 60 * 60


def get_cached_theme_css(theme: Theme) -> str:
    """
    Return rendered CSS for a theme, cached by ETag.

    The cache key includes the theme ETag so DB changes naturally invalidate it.

    Parameters
    ----------
    theme : Theme
        Theme instance.

    Returns
    -------
    str
        Full CSS payload.
    """
    # Import here to avoid circular imports
    from apps.theming.models import Theme  # noqa

    key = f"theme:{theme.slug}:css:{theme.etag}"
    cached = cache.get(key)
    if cached is not None:
        return str(cached)
    css = theme.to_css()
    cache.set(key, css, timeout=CACHE_TTL_SECONDS)
    return css
