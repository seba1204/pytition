from typing import Any

from django.contrib import admin
from django.utils.translation import gettext_lazy

from apps.accounts.models import PytitionUser


@admin.register(PytitionUser)
class PytitionUserAdmin(admin.ModelAdmin):
    list_display = ("name",)

    # Translators: Name of a Pytition user in the admin interface
    @admin.display(description=gettext_lazy("Name"))
    def name(self, pu: Any) -> Any:
        return pu
