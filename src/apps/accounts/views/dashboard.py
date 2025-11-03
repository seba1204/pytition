from django.contrib.auth.decorators import login_required
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import render

from apps.accounts.services import get_session_user


# /user/dashboard
# Dashboard of the logged in user
@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
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
