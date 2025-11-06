"""Services for account-related operations."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from django.contrib.auth.models import User
from django.http import Http404, HttpRequest
from django.utils.translation import gettext as _

if TYPE_CHECKING:
    # import the Django user type
    from django.contrib.auth.models import User

    from apps.accounts.forms import UpdateInfoForm
    from apps.accounts.models import PytitionUser


# Get the user of the current session
def get_session_user(request: HttpRequest) -> PytitionUser:
    """
    Service to get the PytitionUser of the current session.

    Parameters
    ----------
    request : HttpRequest
        The current HTTP request.
    ReturnsUserCreationForm
    -------
    PytitionUser
        The PytitionUser associated with the current session.

    Raises
    ------
    Http404
        If the user is not found.
    """
    # to avoid circular imports
    from apps.accounts.models import PytitionUser  # noqa

    pytitionuser: PytitionUser
    try:
        pytitionuser = PytitionUser.objects.get(user__username=request.user.username)
    except User.DoesNotExist as err:
        raise Http404(_("not found")) from err
    return pytitionuser


def get_update_form(
    user: User, data: Mapping[str, Any] | None = None
) -> UpdateInfoForm:
    """
    Get the UpdateInfoForm for a user with pre-filled data.

    Parameters
    ----------
    user : User
        The user data.
    data : Mapping[str, Any] | None, optional
        The data to populate the form with, by default None.

    Returns
    -------
    UpdateInfoForm
        The populated UpdateInfoForm.

    Raises
    ------
    ImportError
        If the UpdateInfoForm cannot be imported.
    """
    from apps.accounts.forms import UpdateInfoForm  # noqa # to avoid circular import

    if not data:
        _data: dict[str, Any] = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }
    else:
        _data = dict(data)
    return UpdateInfoForm(user, _data)
