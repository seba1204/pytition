from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from apps.accounts.models import Permission
from apps.accounts.routes import AccountsRoute
from apps.accounts.services import get_session_user
from apps.core.exceptions import ApiError
from apps.notifications.services import send_confirmation_email
from apps.organizations.models import Organization
from apps.organizations.routes import OrgRoute
from apps.petitions.helpers import petition_from_id
from apps.petitions.models import Petition
from apps.signatures.models import Signature
from apps.signatures.routes import SignatureRoute


class RedirectError(ApiError):
    """
    Error carrying a redirect target for HTTP views.

    Parameters
    ----------
    message : str
        Human-readable error message (already translated or to be translated upstream).
    redirect_to : str
        URL pattern name to redirect to.
    redirect_args : tuple[Any, ...], optional
        Positional arguments for `redirect()`, by default ().
    """

    status = 400

    def __init__(
        self,
        message: str,
        redirect_to: str,
        redirect_args: tuple[Any, ...] = (),
    ) -> None:
        super().__init__(message)
        self.redirect_to = redirect_to
        self.redirect_args = redirect_args


def _assert_can_view_signatures(
    petition: Petition, pytitionuser: Any
) -> tuple[str, dict[str, Any]]:
    """
    Compute base template and context for a petition signatures page.

    This function centralizes all permission checks and context building
    for both user-owned and organization-owned petitions. It raises a
    `RedirectError` carrying the appropriate redirect destination when
    a check fails.

    Parameters
    ----------
    petition : Petition
        Petition instance to inspect.
    pytitionuser : Any
        Current authenticated user stored in session.

    Returns
    -------
    base_template : str
        Template path to use as a base depending on owner type.
    extra_ctx : dict
        Additional context keys required by org-owned petitions.

    Raises
    ------
    RedirectError
        If user cannot access the signatures for this petition.
    """
    if petition.owner_type == "user":
        if petition.user != pytitionuser:
            raise RedirectError(
                _("You are not allowed to view this petition's signatures."),
                AccountsRoute.DASHBOARD,
            )
        return "accounts/base.html", {}

    org: Organization | None = petition.org
    if org is None:
        raise RedirectError(
            _("Internal error, cannot find the organization owning this petition."),
            AccountsRoute.DASHBOARD,
        )

    if pytitionuser not in org.members.all():
        raise RedirectError(
            _("You are not member of the following organization: %(orgname)s.")
            % {"orgname": org.name},
            AccountsRoute.DASHBOARD,
        )

    try:
        permissions = Permission.objects.get(organization=org, user=pytitionuser)
    except Permission.DoesNotExist as exc:
        raise RedirectError(
            _(
                "Internal error, cannot find your permissions attached to this "
                "organization (%(orgname)s)."
            )
            % {"orgname": org.name},
            AccountsRoute.DASHBOARD,
        ) from exc

    if not permissions.can_view_signatures:
        raise RedirectError(
            _("You are not allowed to view signatures in this organization."),
            OrgRoute.DASHBOARD,
            (org.slugname,),
        )

    other_orgs = pytitionuser.organization_set.filter(~Q(name=org.name)).all()
    extra_ctx: dict[str, Any] = {
        "org": org,
        "other_orgs": other_orgs,
        "user_permissions": permissions,
    }
    return "org/base.html", extra_ctx


def _delete_signatures(signatures: Iterable[Signature], pytitionuser: Any) -> bool:
    """
    Delete signatures with proper permission checks.

    Parameters
    ----------
    signatures : Iterable[Signature]
        Signatures to delete.
    pytitionuser : Any
        Acting user.

    Returns
    -------
    bool
        True if at least one deletion failed due to permissions, False otherwise.
    """
    failed = False
    for s in signatures:
        pet = s.petition
        if pet.org:
            # Organization-owned petition: require specific permission.
            if pet.org.is_allowed_to(pytitionuser, "can_delete_signatures"):
                s.delete()
            else:
                failed = True
        else:
            # User-owned petition: deletion is allowed (legacy behavior).
            s.delete()
    return failed


def _resend_confirmation_for(
    request: HttpRequest, signatures: Iterable[Signature]
) -> bool:
    """
    Re-send confirmation emails for provided signatures.

    Parameters
    ----------
    request : HttpRequest
        Current request (used by `send_confirmation_email`).
    signatures : Iterable[Signature]
        Signatures to process.

    Returns
    -------
    bool
        True if at least one send attempt failed, False otherwise.
    """
    failed = False
    for s in signatures:
        if not s.confirmed:
            try:
                send_confirmation_email(request, s)
            except Exception:
                failed = True
    return failed


def _handle_post_actions(
    request: HttpRequest, petition: Petition, pytitionuser: Any
) -> None:
    """
    Process POST bulk actions on signatures and set flash messages.

    Parameters
    ----------
    request : HttpRequest
        Current request.
    petition : Petition
        Petition owning the signatures.
    pytitionuser : Any
        Acting user.

    Notes
    -----
    This function does not return anything; it only performs side effects
    (DB updates + messages).
    """
    action = request.POST.get("action", "")
    selected_signature_ids = request.POST.getlist("signature_id", "")

    # No-op conditions: nothing selected and not the "re-send-all" action.
    if not action:
        return

    if action == "re-send-all":
        failed = _resend_confirmation_for(
            request,
            Signature.objects.filter(petition=petition, confirmed=False),
        )
        if failed:
            messages.error(
                request,
                _("An error happened while trying to re-send confirmation emails."),
            )
        else:
            messages.success(
                request, _("You successfully re-sent all confirmation emails.")
            )
        return

    if not selected_signature_ids:
        # If we reach here, an action requiring a selection had no IDs.
        messages.error(
            request,
            _("No signatures were selected for the requested action."),
        )
        return

    selected_signatures: QuerySet[Signature] = Signature.objects.filter(
        pk__in=selected_signature_ids
    )

    if action == "delete":
        failed = _delete_signatures(selected_signatures, pytitionuser)
        if failed:
            messages.error(
                request,
                _(
                    "You don't have permission to delete some or all of "
                    "selected signatures."
                ),
            )
        else:
            messages.success(
                request, _("You successfully deleted all selected signatures.")
            )
        return

    if action == "re-send":
        failed = _resend_confirmation_for(request, selected_signatures)
        if failed:
            messages.error(
                request,
                _("An error happened while trying to re-send confirmation emails."),
            )
        else:
            messages.success(
                request,
                _("You successfully re-sent all selected confirmation emails."),
            )
        return

    # Unknown action: keep UX explicit.
    messages.error(request, _("Unknown action requested."))


# Show the signatures of a petition
@login_required
def list_view(request: HttpRequest, petition_id: int) -> HttpResponse:
    """
    Signatures listing and bulk actions for a petition.

    Parameters
    ----------
    request : HttpRequest
        Current HTTP request.
    petition_id : int
        Petition identifier.

    Returns
    -------
    HttpResponse
        Rendered page (GET) or a redirect back to the same page (POST).

    Notes
    -----
    - Guard clauses implement the “happy path”: the main flow is flat,
      errors exit early via a single exception type (`RedirectError`).
    - The number of return statements, branches, and total statements is
      reduced versus the legacy implementation to satisfy the Ruff rules:
      PLR0911, PLR0912, and PLR0915.
    """
    petition: Petition = petition_from_id(petition_id)
    pytitionuser = get_session_user(request)

    try:
        base_template, extra_ctx = _assert_can_view_signatures(petition, pytitionuser)
    except RedirectError as exc:
        messages.error(request, exc.message)
        return redirect(exc.redirect_to, *exc.redirect_args)

    if request.method == "POST":
        _handle_post_actions(request, petition, pytitionuser)
        # Single, unconditional redirect after POST for PRG pattern.
        return redirect(SignatureRoute.LIST, petition_id)

    signatures = petition.signature_set.all()
    ctx: dict[str, Any] = {
        "petition": petition,
        "user": pytitionuser,
        "base_template": base_template,
        "signatures": signatures,
        **extra_ctx,
    }
    return render(request, "signatures/data.html", ctx)
