"""
View to create a new organization.

Uses the OrgCreationForm to handle organization creation.
"""

from typing import TypedDict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

# TODO: move form to apps/organizations/forms.py
from apps.petition.forms import OrgCreationForm

# TODO: move get_session_user to apps/accounts/services.py
from apps.petition.helpers import get_session_user

# TODO: move models to apps/{organizations/accounts}/models.py
from apps.petition.models import Permission, PytitionUser


# Context type hinting
class _OrgCreateContext(TypedDict, total=False):
    user: PytitionUser
    form: OrgCreationForm | None


# GET/POST /org/create
# Create a new organization
@login_required
def org_create(request: HttpRequest) -> HttpResponse:
    # Only super users can create organizations if the setting is on
    if settings.RESTRICT_ORG_CREATION and not request.user.has_perm(
        "petition.add_organization"
    ):
        messages.error(request, _("Only super users can create an organization."))
        # FIXME: should redirect to the page where the user was before requesting
        # the creation of a new organization.
        # If not possible, redirect to user dashboard.
        return redirect("user_dashboard")
    user = get_session_user(request)

    # Context initialization
    ctx: _OrgCreateContext = {
        "user": user,
        "form": None,
    }

    # Handle form submission, if any
    if request.method == "POST":
        form = OrgCreationForm(request.POST)
        if form.is_valid():
            # Form is valid, create the organization in the database
            org = form.save()
            org.members.add(user)
            perm = Permission.objects.get(organization=org)
            perm.set_all(True)
            messages.success(
                request,
                _("You successfully created organization '{}'".format(org.name)),
            )
            # FIXME: should redirect to the newly created org dashboard.
            return redirect("user_dashboard")
        else:
            # Form is not valid, show it with errors in the template
            ctx.update({"form": form})
            return render(request, "petition/org_create.html", ctx)

    # If GET request, show an empty form
    form = OrgCreationForm()
    ctx.update({"form": form})
    return render(request, "petition/org_create.html", ctx)
