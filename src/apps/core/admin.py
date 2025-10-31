from django.contrib import admin

from apps.accounts.models import Permission
from apps.petitions.models import SlugModel


# TODO: should be moved to petitions app
@admin.register(SlugModel)
class SlugModelAdmin(admin.ModelAdmin):
    pass


# TODO: should be moved to accounts app
@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    pass
