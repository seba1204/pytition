from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _

from apps.petition.helpers import get_session_user, petition_from_id
from apps.petitions.routes import PetitionsRoute


# /<int:petition_id>/add_new_slug
# Add a new slug for a petition
@login_required
def add_slug(request: HttpRequest, petition_id: int) -> HttpResponse:
    pytitionuser = get_session_user(request)
    try:
        petition = petition_from_id(petition_id)
    except Exception:
        messages.error(request, _("This petition does not exist (anymore?)."))
        return redirect("user_dashboard")

    if request.method == "POST":
        slug_texts = request.POST.getlist("slugtext", "")
        if slug_texts in ("", []):
            messages.error(request, _("You entered an empty slug text"))
        elif petition.is_allowed_to_edit(pytitionuser):
            for slugtext in slug_texts:
                try:
                    petition.add_slug(slugtext)
                    petition.save()
                    messages.success(
                        request,
                        _("Successful addition of the slug '{}'!".format(slugtext)),
                    )
                except IntegrityError:
                    messages.error(
                        request, _("The slug '{}' already exists!".format(slugtext))
                    )
                except ValidationError as v:
                    for message in v.messages:
                        messages.error(request, message)
        else:
            messages.error(
                request, _("You don't have the permission to modify petitions")
            )
        return redirect(
            reverse(PetitionsRoute.EDIT, args=[petition_id])
            + "#tab_social_network_form"
        )
    else:
        return redirect("user_dashboard")
