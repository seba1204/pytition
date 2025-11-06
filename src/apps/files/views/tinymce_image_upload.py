"""TinyMCE image upload view."""

from __future__ import annotations

import hashlib
from typing import TypedDict

from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt

INCLUDE_ORIGINAL_FILENAME = False


class UploadResponse(TypedDict):
    """
    TinyMCE upload response.

    Attributes
    ----------
    location : str
        Public URL where the uploaded image is accessible.
    """

    location: str


def save_file(file: UploadedFile, path: str) -> str:
    """Save uploaded file if not already present, return the saved path."""
    if not default_storage.exists(path):
        path = default_storage.save(path, file)
    return path


def compute_hash(data: bytes) -> str:
    """Compute a simple hash of the given data."""
    return hashlib.sha256(data).hexdigest()


@login_required
@csrf_exempt
def tinymce_image_upload(
    request: HttpRequest,
) -> JsonResponse | HttpResponseBadRequest:
    """
    Handle TinyMCE image uploads.

    Notes
    -----
    - Expects a POST with a file field named 'file' (TinyMCE default).
    - Saves via Django's default storage and returns a JSON with the 'location' key.
    - Stores files under <media>/<filename>-<hash>.<ext>
        if INCLUDE_ORIGINAL_FILENAME is True,
        else <media>/<hash>.<ext>.
    - If the same file is uploaded multiple times, it won't be duplicated.
    - Hash is computed from file, ensuring identical files map to the same storage path.

    Returns
    -------
    JsonResponse | HttpResponseBadRequest
        JSON containing {'location': '<public-url>'} or 400 if invalid.
    """
    if request.method != "POST" or "file" not in request.FILES:
        return HttpResponseBadRequest(_("Invalid request."))

    uploaded: UploadedFile | list[object] = request.FILES["file"]

    # If multiple files are uploaded take the first one (TinyMCE default is single file)
    if isinstance(uploaded, list):
        if uploaded and isinstance(uploaded[0], UploadedFile):
            uploaded = uploaded[0]
        else:
            return HttpResponseBadRequest(_("Invalid file upload."))

    file_data: bytes = uploaded.read()
    file_hash: str = compute_hash(file_data)
    uploaded.seek(0)  # Reset file pointer after reading

    # Extract file extension
    original_name: str = uploaded.name or "uploaded_file"
    if "." in original_name:
        name_part, ext_part = original_name.rsplit(".", 1)
        ext_part = "." + ext_part
    else:
        name_part = original_name
        ext_part = ""

    # Truncate name to avoid overly long filenames
    name_part = name_part[:50]

    # Generate storage path
    storage_path = (
        f"{name_part}-{file_hash}{ext_part}"
        if INCLUDE_ORIGINAL_FILENAME
        else f"{file_hash}{ext_part}"
    )

    # Save file
    saved_path = save_file(uploaded, storage_path)
    public_url = default_storage.url(saved_path)
    response: UploadResponse = {"location": public_url}
    return JsonResponse(response)
