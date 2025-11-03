from django.contrib import admin

from apps.consents.admin import confirm
from apps.notifications.admin import resend_confirmation_mail
from apps.signatures.models import Signature


@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "phone",
        "email",
        "confirmed",
        "subscribed_to_mailinglist",
        "petition",
        "date",
    )
    list_filter = ("petition", "confirmed")
    actions = [confirm, resend_confirmation_mail]
    search_fields = ("first_name", "last_name", "phone", "email")
    change_form_template = "signatures/change_form.html"
