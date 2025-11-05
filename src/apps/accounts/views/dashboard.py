""""Views for the user dashboard."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.accounts.services import get_session_user


# Dashboard of the logged in user
@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """
    Render the user dashboard with their petitions.

    Parameters
    ----------
    request : HttpRequest
        The current HTTP request.
    Returns
    -------
    HttpResponse
        The rendered dashboard page.
    """
    user = get_session_user(request)
    petitions = user.petition_set.all()

    return render(
        request,
        "accounts/dashboard.html",
        {
            "user": user,
            "petitions": petitions,
            "can_create_petition": True,
            "displaying_dashboard": True,
        },
    )
