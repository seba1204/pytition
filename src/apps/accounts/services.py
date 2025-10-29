from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.http import Http404, HttpRequest
from django.utils.translation import gettext as _

if TYPE_CHECKING:
    from apps.petition.models import PytitionUser


# Get the user of the current session
def get_session_user(request: HttpRequest) -> PytitionUser:
    """
    Service to get the PytitionUser of the current session.

    Parameters
    ----------
    request : HttpRequest
        The current HTTP request.
    Returns
    -------
    PytitionUser
        The PytitionUser associated with the current session.
    Raises
    ------
    Http404
        If the user is not found.
    """

    # to avoid circular imports
    from apps.petition.models import PytitionUser  # noqa

    pytitionuser: PytitionUser
    try:
        pytitionuser = PytitionUser.objects.get(user__username=request.user.username)
    except User.DoesNotExist as err:
        raise Http404(_("not found")) from err
    return pytitionuser
