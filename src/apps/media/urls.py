from __future__ import annotations

from django.urls import URLPattern

from apps.core.routes import Route, build_urlpatterns, validate_bijection
from apps.media import views as MdV
from apps.media.routes import MediaRoute

app_name = "media"

# --------------------------------------------------------------------------- #
# One-to-one mapping: every MediaRoute must appear exactly once
# --------------------------------------------------------------------------- #

ROUTES: dict[MediaRoute, Route] = {
    MediaRoute.UPLOAD: Route("upload", MdV.upload),
}

# Fail fast at import time (CI-friendly)
validate_bijection(MediaRoute, ROUTES)

# Short-named patterns; the namespace is supplied by include(..., namespace=NAMESPACE)
urlpatterns: list[URLPattern] = build_urlpatterns(ROUTES)
