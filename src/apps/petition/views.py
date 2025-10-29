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
def image_upload(request: HttpRequest) -> HttpResponse:
    pytitionuser = get_session_user(request)

    if request.method != "POST":
        return HttpResponseForbidden()

    file = request.FILES.get("file", "")
    if file == "":
        return HttpResponseForbidden()

    storage = FileSystemStorage()
    path = Path(pytitionuser.username) / file.name
    name = storage.save(str(path), file)
    return JsonResponse({"location": storage.url(name)})
