"""View to resend petition signature confirmation emails."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from apps.notifications.services import send_confirmation_email
from apps.signatures.models import Signature


# resend/<int:signature_id>
# resend the signature confirmation email
@login_required
def resend(request: HttpRequest, petition_id: int, signature_id: int) -> HttpResponse:
    """
    Resend the confirmation email for a signature.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    signature_id : int
        The ID of the signature to resend the confirmation email for.
    Returns
    -------
    HttpResponse
        A redirect response to the admin change page for the signature.
    """

    app_label = Signature._meta.app_label
    signature = Signature.objects.filter(pk=signature_id).get()
    send_confirmation_email(request, signature)
    return redirect(f"admin:{app_label}_signature_change", signature_id)
