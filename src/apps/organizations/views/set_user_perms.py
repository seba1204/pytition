"""View to change user permissions in an organization."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import redirect
from django.utils.translation import gettext as _

# TODO: move models to apps/{organizations/accounts}/models.py
from apps.accounts.models import Permission
from apps.accounts.routes import AccountsRoute
from apps.accounts.services import get_session_user
from apps.organizations.models import Organization
from apps.organizations.routes import OrgRoute
from apps.petition.models import PytitionUser

# PATH /org/<slug:orgslugname>/set_user_permissions/<slug:user_name>
# Set a permission for an user


@login_required
# FIXME: refactor to avoid those warnings
# Too many return statements (7 > 6)
# Too many branches (13 > 12)
# Too many statements (54 > 50)
def set_user_perms(  # noqa
    request: HttpRequest, orgslugname: str, user_name: str
) -> HttpResponse:
    """
    Actually do the modification of user permissions.

    Data come from "org_edit_user_perms" view's form.
    """
    pytitionuser = get_session_user(request)

    try:
        org = Organization.objects.get(slugname=orgslugname)
    except Organization.DoesNotExist:
        raise Http404(_("Organization does not exist")) from None

    if pytitionuser not in org.members.all():
        messages.error(request, _("You are not part of this organization"))
        return redirect(AccountsRoute.DASHBOARD)

    try:
        user_perms = Permission.objects.get(user=pytitionuser, organization=org)
    except Exception:
        messages.error(
            request,
            _(
                "Fatal error, you don't have permissions attached to you for "
                "this organization"
            ),
        )
        return redirect(OrgRoute.DASHBOARD, org.slugname)

    if not user_perms.can_modify_permissions:
        messages.error(
            request,
            _("You are not allowed to modify this organization members' permissions"),
        )
        return redirect(OrgRoute.EDIT_USER_PERMS, orgslugname, user_name)

    try:
        member = PytitionUser.objects.get(user__username=user_name)
    except PytitionUser.DoesNotExist:
        messages.error(request, _("User does not exist"))
        return redirect(OrgRoute.DASHBOARD, orgslugname)

    if org not in member.organization_set.all():
        messages.error(
            request,
            _(
                "This user is not part of organization '{orgname}'".format(
                    orgname=org.name
                )
            ),
        )
        return redirect(OrgRoute.DASHBOARD, org.slugname)

    try:
        permissions = Permission.objects.get(user=member, organization=org)
    except Permission.DoesNotExist:
        messages.error(
            request,
            _(
                "Fatal error, this user does not have permissions attached for "
                "this organization"
            ),
        )
        return redirect(OrgRoute.DASHBOARD, org.slugname)

    if request.method == "POST":
        error = False
        post = request.POST
        permissions.can_remove_members = post.get("can_remove_members", "") == "on"
        permissions.can_add_members = post.get("can_add_members", "") == "on"
        permissions.can_create_petitions = post.get("can_create_petitions", "") == "on"
        permissions.can_modify_petitions = post.get("can_modify_petitions", "") == "on"
        permissions.can_delete_petitions = post.get("can_delete_petitions", "") == "on"
        permissions.can_create_templates = post.get("can_create_templates", "") == "on"
        permissions.can_modify_templates = post.get("can_modify_templates", "") == "on"
        permissions.can_delete_templates = post.get("can_delete_templates", "") == "on"
        permissions.can_view_signatures = post.get("can_view_signatures", "") == "on"
        permissions.can_modify_signatures = (
            post.get("can_modify_signatures", "") == "on"
        )
        permissions.can_delete_signatures = (
            post.get("can_delete_signatures", "") == "on"
        )
        can_modify_perms = post.get("can_modify_permissions", "") == "on"
        with transaction.atomic():
            # if user is dropping his own permissions
            if (
                not can_modify_perms
                and permissions.can_modify_permissions
                and pytitionuser == member
            ):
                # get list of people with can_modify_permissions permission on this org
                owners = org.owners
                if owners.count() > 1:
                    permissions.can_modify_permissions = can_modify_perms
                elif org.members.count() > 1:
                    error = True
                    messages.error(
                        request,
                        _(
                            "You cannot remove your ability to change permissions on "
                            "this Organization because you are the only one left who "
                            "can do this. Give the permission to someone else before "
                            "removing yours."
                        ),
                    )
                else:
                    error = True
                    messages.error(
                        request,
                        _(
                            "You cannot remove your ability to change permissions on "
                            "this Organization because you are the only member left."
                        ),
                    )
        if not error:
            permissions.can_modify_permissions = can_modify_perms
            messages.success(request, _("Permissions successfully changed!"))
        permissions.save()

    return redirect(OrgRoute.EDIT_USER_PERMS, orgslugname, user_name)
