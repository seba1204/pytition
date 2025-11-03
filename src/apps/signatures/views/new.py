from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.html import format_html
from django.utils.timezone import now
from django.utils.translation import gettext as _

from apps.consents.helpers import subscribe_to_newsletter
from apps.core.helpers import get_client_ip
from apps.notifications.services import send_confirmation_email
from apps.petitions.helpers import (
    check_petition_is_accessible,
    petition_detail_meta,
    petition_from_id,
)
from apps.signatures.forms import SignatureForm
from apps.signatures.models import Signature


# Sign a petition (create  a new signature)
def new(request: HttpRequest, petition_id: int) -> HttpResponse:
    """
    Create a signature for a petition.

    Parameters:
    -----------
    request : HttpRequest
        The HTTP request object
    petition_id : int
        The ID of the petition to sign
    Returns:
    --------
    HttpResponse
        A redirect to the petition detail page
    """
    petition = petition_from_id(petition_id)
    check_petition_is_accessible(request, petition)

    if request.method == "POST":
        form = SignatureForm(petition=petition, data=request.POST)
        ctx = {
            "petition": petition,
            "form": form,
            "meta": petition_detail_meta(request, petition_id),
            "og_image_absolute_url": request.build_absolute_uri(petition.twitter_image),
        }
        if not form.is_valid():
            return render(request, "petitions/detail.html", ctx)

        ipaddr = make_password(
            get_client_ip(request),
            salt=petition.salt.encode("utf-8"),  # type: ignore[arg-type]
        )
        since = now() - timedelta(seconds=settings.SIGNATURE_THROTTLE_TIMING)
        signatures = Signature.objects.filter(
            petition=petition, ipaddress=ipaddr, date__gt=since
        )
        if signatures.count() > settings.SIGNATURE_THROTTLE:
            messages.error(
                request,
                _("Too many signatures from your IP address, please try again later."),
            )
            return render(request, "petitions/detail.html", ctx)
        else:
            signature = form.save()
            signature.ipaddress = ipaddr
            signature.save()
            send_confirmation_email(request, signature)
            messages.success(
                request,
                format_html(
                    _(
                        "Thank you for signing this petition, an email has just been "
                        "sent to you at your address %(email)s "
                        "in order to confirm your signature."
                        "<br>"
                        "You will need to click on the confirmation link in the email."
                        "<br>"
                        "If you cannot find the email in your Inbox, please have a "
                        "look in your Spam box."
                    )
                    % {"email": signature.email}
                ),
            )

        if petition.has_newsletter and signature.subscribed_to_mailinglist:
            subscribe_to_newsletter(petition, signature.email)

    return redirect(petition.url)
