"""Creation view for Petition (unified render template)."""

from __future__ import annotations

from typing import Any, TypedDict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from apps.accounts.models import PytitionUser
from apps.accounts.services import get_session_user
from apps.petitions.models import Petition


class PetitionCreatePayload(TypedDict, total=False):
    """
    Payload to create a petition.

    Notes
    -----
    The ownership (user/org) can be set later; for a simple UX the
    petition is created for the current user by default.
    """

    title: str
    text: str
    tagline: str


@login_required
def new(request: HttpRequest) -> HttpResponse:
    """
    Create a new petition and render in edit mode.

    Parameters
    ----------
    request : HttpRequest
        Incoming request.

    Returns
    -------
    HttpResponse
        Redirects to edit on POST, or renders an unsaved draft on GET.
    """
    pytitionuser: PytitionUser = get_session_user(request)

    if request.method == "POST":
        title: str | None = request.POST.get("title")
        text: str | None = request.POST.get("text")
        tagline: str | None = request.POST.get("tagline")

        petition: Petition = Petition()
        petition.user = pytitionuser
        petition.title = title or _("Untitled")
        petition.text = text or ""
        petition.tagline = tagline or ""

        file_obj: UploadedFile | None = request.FILES.get("illustration")
        if file_obj is not None:
            petition.illustration = file_obj
        petition.save()
        messages.success(request, _("Petition created."))
        return redirect("petitions:edit", petition_id=petition.id)

    temp: Petition = Petition(title=_("Untitled"), text="", tagline="")
    context: dict[str, Any] = {
        "petition": temp,
        "mode": "edit",
        "can_edit": True,
    }
    return render(request, "petitions/render.html", context)
