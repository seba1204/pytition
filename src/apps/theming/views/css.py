"""View to confirm petition signatures."""

from __future__ import annotations

from datetime import UTC

from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseNotModified,
)
from django.shortcuts import get_object_or_404
from django.utils.http import http_date, parse_http_date_safe

from apps.theming.models import Theme
from apps.theming.permissions import theme_can_view
from apps.theming.services import get_cached_theme_css


# Confirm signature to a petition
def css(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Serve compiled CSS for a Theme with conditional caching.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request object.
    slug : str
        The slug identifying the Theme to render.

    Returns
    -------
    HttpResponse
        A response containing the rendered CSS, or a 304/404 response
        depending on caching and access control conditions.

    Notes
    -----
    - Checks if the theme is public or accessible to the current user.
    - Supports conditional GET via ETag and Last-Modified headers.
    - Sets proper Cache-Control directives for public/private themes.
    """
    theme = get_object_or_404(Theme, slug=slug)

    if not theme_can_view(
        request.user if request.user.is_authenticated else None, theme
    ):
        # Update policy: 404 or 403. 404 leaks less info.
        raise Http404("Theme not found")

    # Conditional request handling: If-None-Match
    etag = theme.etag
    inm = request.headers.get("If-None-Match")
    if inm and inm.strip() == etag:
        return HttpResponseNotModified()

    # Conditional request handling: If-Modified-Since (secondary)
    ims = request.headers.get("If-Modified-Since")
    if ims:
        ims_ts = parse_http_date_safe(ims)
        if ims_ts is not None:
            last_mod_ts = int(theme.updated_at.replace(tzinfo=UTC).timestamp())
            if last_mod_ts <= ims_ts:
                return HttpResponseNotModified()

    css = get_cached_theme_css(theme)

    resp = HttpResponse(css, content_type="text/css; charset=utf-8")
    resp["ETag"] = etag
    resp["Last-Modified"] = http_date(
        int(theme.updated_at.replace(tzinfo=UTC).timestamp())
    )
    if theme.is_public:
        resp["Cache-Control"] = "public, max-age=3600, must-revalidate"
    else:
        resp["Cache-Control"] = "private, no-cache, max-age=0, must-revalidate"
    return resp
