from typing import Any

from django.contrib import admin
from django.utils.translation import gettext_lazy

from apps.notifications.services import send_confirmation_email


@admin.action(description=gettext_lazy("Send the confirmation email once again"))
def resend_confirmation_mail(modeladmin: Any, request: Any, queryset: Any) -> None:
    for signature in queryset:
        send_confirmation_email(request, signature)
