"""Django Admin definition for Theme."""

from __future__ import annotations

from typing import Any, TypedDict

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpRequest, JsonResponse
from django.urls import URLPattern, path

from apps.theming.admin.forms import ThemeAdminForm
from apps.theming.models import Theme


class _OwnerOption(TypedDict):
    """JSON shape for owner-object dropdown options."""

    id: str
    label: str


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ``Theme`` model.

    The form provides a dynamic ``owner_object`` selector that responds to
    changes in ``owner_content_type`` via a small AJAX endpoint.
    """

    form = ThemeAdminForm

    # Display and edit layout
    list_display = (
        "name",
        "slug",
        "creator",
        "owner_content_type",
        "owner_object_id",
        "is_public",
        "updated_at",
    )
    search_fields = ("name", "slug", "description", "creator__username")
    list_filter = ("is_public", "owner_content_type")
    readonly_fields = ("etag", "created_at", "updated_at")

    # Field order in the form (include virtual owner_object field)
    fields = (
        "name",
        "slug",
        "description",
        "creator",
        "owner_content_type",
        "owner_object",  # virtual field for UI
        "owner_object_id",  # hidden, kept in sync by the form
        "tokens_schema_version",
        "tokens_css",
        "components_css",
        "is_public",
        "etag",
        "created_at",
        "updated_at",
    )

    class Media:
        """Attach custom admin JS."""

        js = ("js/theming/owner_picker.js",)

    # ----- Lightweight AJAX endpoint --------------------------------------------
    def get_urls(self) -> list[URLPattern]:
        """
        Extend admin URLs with an endpoint to fetch owner objects for a CT.

        Returns
        -------
        list[URLPattern]
            The default ModelAdmin URLs plus a JSON endpoint.
        """
        urls = super().get_urls()
        extra = [
            path(
                "owner-objects/",
                self.admin_site.admin_view(self.owner_objects_view),
                name="theming_theme_owner_objects",
            )
        ]
        return extra + urls

    def owner_objects_view(self, request: HttpRequest) -> JsonResponse:
        """
        Return a JSON array of possible owner objects for a given ContentType.

        Parameters
        ----------
        request : HttpRequest
            The incoming request, expected to contain ``ct`` (int) and optional
            ``q`` (str) for basic label filtering.

        Returns
        -------
        JsonResponse
            Response of the form ``{"results": [{"id": "...","label":"..."}]}``.

        Notes
        -----
        - This endpoint is intentionally simple; it limits results to 50 items.
        - Basic ``icontains`` search is attempted on a few common label fields.
        """
        ct_param = request.GET.get("ct")
        query = (request.GET.get("q") or "").strip()
        if not ct_param:
            return JsonResponse({"results": []})

        try:
            ct = ContentType.objects.get(pk=int(ct_param))
        except (ValueError, ContentType.DoesNotExist):
            return JsonResponse({"results": []})

        model_cls = ct.model_class()
        if model_cls is None:
            return JsonResponse({"results": []})

        qs = model_cls._default_manager.all()
        # Very light filtering on typical text fields if a query is provided.
        if query:
            # Try common name-like fields; fall back to str(instance) filter in JS.
            name_fields = [
                f
                for f in ("name", "title", "username")
                if f in {fld.name for fld in model_cls._meta.fields}
            ]
            if name_fields:
                q_obj = Q()
                for f in name_fields:
                    q_obj |= Q(**{f"{f}__icontains": query})
                qs = qs.filter(q_obj)

        qs = qs.order_by("pk")[:50]

        def as_label(obj: Any) -> str:
            # Use a compact label friendly for dropdowns.
            return f"{obj} (#{obj.pk})"

        results: list[_OwnerOption] = [
            {"id": str(obj.pk), "label": as_label(obj)} for obj in qs
        ]
        return JsonResponse({"results": results})
