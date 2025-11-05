"""User account settings view."""

from typing import TypedDict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from apps.accounts.forms import DeleteAccountForm, UpdateInfoForm
from apps.accounts.models import PytitionUser
from apps.accounts.services import get_session_user, get_update_form
from apps.organizations.models import Organization


class _SettingsContext(TypedDict, total=False):
    user: PytitionUser | None
    update_info_form: UpdateInfoForm | None
    update_info_form_submitted: bool | None
    delete_account_form: DeleteAccountForm | None
    delete_account_form_submitted: bool | None
    password_change_form: PasswordChangeForm | None
    password_change_form_submitted: bool | None
    base_template: str | None
    orgs: QuerySet[Organization, Organization] | None


# FIXME: [#76, #79] split into multiple functions helpers, services, etc.
@login_required
def settings(request: HttpRequest) -> HttpResponse:  # noqa
    """Show and process the user settings page."""
    ctx: _SettingsContext
    pytitionuser = get_session_user(request)
    submitted_ctx: _SettingsContext = {
        "update_info_form_submitted": False,
        "delete_account_form_submitted": False,
        "password_change_form_submitted": False,
    }

    if request.method == "POST":
        if "update_info_form_submitted" in request.POST:
            update_info_form = UpdateInfoForm(pytitionuser.user, request.POST)
            submitted_ctx["update_info_form_submitted"] = True
            if update_info_form.is_valid():
                update_info_form.save()
        else:
            update_info_form = get_update_form(pytitionuser.user)

        if "delete_account_form_submitted" in request.POST:
            delete_account_form = DeleteAccountForm(request.POST)
            submitted_ctx["delete_account_form_submitted"] = True
            if delete_account_form.is_valid():
                pytitionuser.drop()
                return redirect("index")
        else:
            delete_account_form = DeleteAccountForm()

        if "password_change_form_submitted" in request.POST:
            password_change_form = PasswordChangeForm(pytitionuser.user, request.POST)
            submitted_ctx["password_change_form_submitted"] = True
            if password_change_form.is_valid():
                password_change_form.save()
                messages.success(request, _("You successfully changed your password!"))
        else:
            password_change_form = PasswordChangeForm(pytitionuser.user)

    else:
        update_info_form = get_update_form(pytitionuser.user)
        delete_account_form = DeleteAccountForm()
        password_change_form = PasswordChangeForm(pytitionuser.user)

    orgs: QuerySet[Organization, Organization] = pytitionuser.organization_set.all()
    # Checking if the user is allowed to leave the organization

    MIN_ORG_MEMBERS = 2

    for org in orgs:
        if org.members.count() < MIN_ORG_MEMBERS:
            can_leave = False
        else:
            # More than one user, we need to check owners
            owners = org.owners.all()
            if owners.count() == 1 and pytitionuser in owners:
                can_leave = False
            else:
                can_leave = True
        # Add a dynamic attribute to the organization
        org.leave = can_leave  # type: ignore

    ctx = {
        "user": pytitionuser,
        "update_info_form": update_info_form,
        "delete_account_form": delete_account_form,
        "password_change_form": password_change_form,
        "base_template": "accounts/base.html",
        "orgs": orgs,
    }

    ctx.update(submitted_ctx)

    return render(request, "accounts/settings.html", ctx)
