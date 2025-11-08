"""Edit view for Petition (unified render template)."""

from __future__ import annotations

from typing import Any, TypedDict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from apps.accounts.services import get_session_user
from apps.petitions.models import Petition


class PetitionPayload(TypedDict, total=False):
    """
    Incoming payload to update a petition.

    Notes
    -----
    This payload intentionally keeps only the fields that belong to
    the Petition itself; authors/resources/news have dedicated endpoints.
    """

    title: str
    text: str
    tagline: str


@login_required
def edit(request: HttpRequest, petition_id: int) -> HttpResponse:
    """
    Edit a petition using the unified template.

    Parameters
    ----------
    request : HttpRequest
        Incoming request.
    petition_id : int
        ID of the petition to edit.

    Returns
    -------
    HttpResponse
        Rendered page in edit mode on GET, or redirects on successful POST.
    """
    petition: Petition = get_object_or_404(Petition, pk=petition_id)
    pytitionuser = get_session_user(request)
    if not petition.is_allowed_to_edit(pytitionuser):
        return HttpResponseForbidden()

    if request.method == "POST":
        payload: PetitionPayload = {}
        title: str | None = request.POST.get("title")
        text: str | None = request.POST.get("text")
        tagline: str | None = request.POST.get("tagline")
        if title is not None:
            payload["title"] = title
        if text is not None:
            payload["text"] = text
        if tagline is not None:
            payload["tagline"] = tagline

        for k, v in payload.items():
            setattr(petition, k, v)

        file_obj: UploadedFile | None = request.FILES.get("illustration")
        if file_obj is not None:
            petition.illustration = file_obj

        petition.save()
        messages.success(request, _("Petition updated."))
        return redirect("petitions:detail", petition_id=petition.id)

    context: dict[str, Any] = {
        "petition": petition,
        "mode": "edit",
        "can_edit": True,
    }
    return render(request, "petitions/render.html", context)
