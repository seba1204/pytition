import csv

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse

from apps.accounts.services import get_session_user
from apps.petitions.models import Petition
from apps.signatures.models import Signature


# returns the CSV files of the list of signatures
@login_required
def export(request: HttpRequest, petition_id: int) -> HttpResponse:
    user = get_session_user(request)
    try:
        petition = Petition.objects.get(pk=petition_id)
    except Petition.DoesNotExist:
        return JsonResponse({}, status=404)
    org = petition.org
    is_allowed = False
    if org is not None:
        is_allowed = org.is_allowed_to(user, "can_view_signatures")
    if (
        petition.owner_type == "org"
        and not is_allowed
        or petition.owner_type == "user"
        and petition.owner != user
    ):
        return JsonResponse({}, status=403)

    filename = f"{petition}.csv"
    signatures = Signature.objects.filter(petition=petition)
    confirmed = request.GET.get("confirmed", "").lower() in ["true", "1", "yes"]

    signatures = signatures.filter(confirmed=True) if confirmed else signatures.all()
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment;filename={filename}".replace(
        "\r\n", ""
    ).replace(" ", "%20")
    writer = csv.writer(response)
    attrs = [
        "first_name",
        "last_name",
        "phone",
        "email",
        "subscribed_to_mailinglist",
        "confirmed",
    ]
    writer.writerow(attrs)
    for signature in signatures:
        values = [getattr(signature, field) for field in attrs]
        writer.writerow(values)
    return response
