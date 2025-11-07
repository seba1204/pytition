"""Single-step petition creation view."""

from __future__ import annotations

from typing import cast

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from apps.accounts.routes import AccountsRoute
from apps.accounts.services import get_session_user
from apps.petitions.forms.create_single import PetitionCreateForm
from apps.petitions.models import Petition
from apps.petitions.routes import PetitionsRoute


@login_required(login_url="accounts:login")
def new(request: HttpRequest, orgslugname: str | None = None) -> HttpResponse:
    """
    Create a petition in one step.

    Parameters
    ----------
    request : HttpRequest
        Incoming request.
    orgslugname : str | None
        Optional organization slug; when provided, the petition will
        be created under that organization. Otherwise it is owned by the user.

    Returns
    -------
    HttpResponse
        Rendered page or redirect after successful creation.
    """
    # Enforce user-petition disable flag
    if settings.DISABLE_USER_PETITION and orgslugname is None:
        messages.error(
            request, _("Users are not allowed to create their own petitions.")
        )
        return redirect(AccountsRoute.DASHBOARD)

    if request.method == "POST":
        form = PetitionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = get_session_user(request)
            illustration: UploadedFile | None = cast(
                UploadedFile | None, form.cleaned_data.get("illustration")
            )
            pet = Petition(
                title=form.cleaned_data["title"],
                text=form.cleaned_data.get("text") or "",
            )
            if orgslugname:
                pet.org_slug = orgslugname  # type: ignore[attr-defined]
            else:
                pet.user = user
            # Persist first, then attach file if provided
            pet.save()
            if illustration:
                # Save to ImageField if available (illustration)
                # or fallback to twitter_image path.
                if hasattr(pet, "illustration"):
                    pet.illustration = illustration
                else:
                    pet.twitter_image = illustration.name or ""
                pet.save()

            messages.success(request, _("Petition created."))
            return redirect(PetitionsRoute.DETAIL, petition_id=pet.id)
    else:
        form = PetitionCreateForm()
    print("Rendering new petition form")
    return render(
        request,
        "petitions/new.html",
        {
            "form": form,
            "orgslugname": orgslugname,
        },
    )
