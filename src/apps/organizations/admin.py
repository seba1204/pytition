from typing import Any

from django.contrib import admin
from django.utils.translation import gettext_lazy

from apps.organizations.models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "petition_num", "user_num")

    @admin.display(description=gettext_lazy("Number of petitions"))
    def petition_num(self, org: Any) -> int:
        return int(org.petition_set.count())

    @admin.display(description=gettext_lazy("Number of members"))
    def user_num(self, org: Any) -> int:
        return int(org.members.count())
