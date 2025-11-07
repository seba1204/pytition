"""URL routing for the Files application."""

from __future__ import annotations

from apps.core.route import Route, build_urlpatterns, validate_bijection
from apps.files import views as FV
from apps.files.routes import FilesRoute

app_name = "files"

# --------------------------------------------------------------------------- #
# One-to-one mapping: every FilesRoute must appear exactly once
# --------------------------------------------------------------------------- #

ROUTES: dict[FilesRoute, Route] = {
    FilesRoute.UPLOAD: Route("upload", FV.upload),
    FilesRoute.TINYMCE: Route("tinymce", FV.tinymce_image_upload),
}

# Fail fast at import time (CI-friendly)
validate_bijection(FilesRoute, ROUTES)

# Short-named patterns; the namespace is supplied by include(..., namespace=NAMESPACE)
urlpatterns = build_urlpatterns(ROUTES)
