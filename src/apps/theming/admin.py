"""Theme admin interface."""

from django.contrib import admin

from .models import Theme


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    """Admin for Theme model."""

    list_display = (
        "name",
        "slug",
        "creator",
        "owner_content_type",
        "owner_object_id",
        "updated_at",
    )
    search_fields = (
        "name",
        "slug",
        "description",
        "creator__username",
        "owner_object_id",
    )
    list_select_related = ("owner_content_type",)
    readonly_fields = ("etag", "created_at", "updated_at")
    ordering = ("-updated_at",)
    fieldsets = (
        (None, {"fields": ("name", "slug", "description")}),
        (
            "Ownership",
            {
                "fields": (
                    "creator",
                    "owner_content_type",
                    "owner_object_id",
                )
            },
        ),
        (
            "Timestamps and caching",
            {"fields": ("etag", "created_at", "updated_at")},
        ),
    )
