from typing import Any

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy


# Translators: Admin action to confirm signatures
@admin.action(description=gettext_lazy("Confirm the signatures"))
def confirm(modeladmin: Any, request: Any, queryset: Any) -> None:
    try:
        for signature in queryset:
            signature.confirm()
            signature.save()
    except ValidationError as e:
        messages.error(request, gettext_lazy("Error: %(error)s") % {"error": e})
