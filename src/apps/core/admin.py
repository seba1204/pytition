from django.contrib import admin

from apps.petition.models import (
    Permission,
    SlugModel,
)


@admin.register(SlugModel)
class SlugModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    pass
