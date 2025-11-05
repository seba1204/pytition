"""Views for handling file uploads."""

from datetime import datetime
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
)

from apps.accounts.services import get_session_user


@login_required
def upload(request: HttpRequest) -> HttpResponse:
    """Handle image upload from TinyMCE editor."""
    pytitionuser = get_session_user(request)

    if request.method != "POST":
        return HttpResponseForbidden()

    file = request.FILES.get("file", None)
    if file is None or not hasattr(file, "name") or file.name is None:
        return HttpResponseForbidden()

    storage = FileSystemStorage()
    default_name: str
    if not file.name:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"uploaded_{ts}.dat"
    path = Path(pytitionuser.username) / (file.name or default_name)
    name = storage.save(str(path), file)
    return JsonResponse({"location": storage.url(name)})
