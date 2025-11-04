"""Helper functions for signature handling."""

from typing import Any

from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import HttpRequest


def hide_sign_form_if_user_just_signed(
    request: HttpRequest, ctx: dict[str, Any]
) -> None:
    """
    Helper function to hide the sign form if the user has just signed the petition.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    ctx : dict[str, Any]
        The context dictionary to update.
    """

    storage = get_messages(request)
    for message in storage:
        if message.level == messages.SUCCESS:
            just_confirmed = request.session.get("just_confirmed", False)
            if just_confirmed:
                ctx.update({"signature_is_confirmed": True})
                request.session["just_confirmed"] = False
            else:
                ctx.update({"petition_is_signed": True})
