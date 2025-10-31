from django.contrib import admin

from apps.accounts.models import Permission
from apps.petition.models import SlugModel


@admin.register(SlugModel)
class SlugModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    pass
