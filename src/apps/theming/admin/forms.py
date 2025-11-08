"""Admin forms for theming app."""

from __future__ import annotations

from typing import Any, cast

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import Model, QuerySet
from django.urls import reverse

from apps.theming.models import Theme


class ThemeAdminForm(forms.ModelForm):
    """
    ModelForm used in Django Admin for ``Theme``.

    It exposes a dynamic ``owner_object`` select that is populated based on the
    currently selected ``owner_content_type``. The form also keeps a hidden
    ``owner_object_id`` field synchronized for persistence.

    Notes
    -----
    - All validation is done early so that ``Model.clean`` passes in admin.
    - ``owner_object`` is never saved directly to the DB; instead,
      ``owner_object_id`` is updated from the selected object.
    """

    owner_object_id: forms.CharField = forms.CharField(
        required=False,
        widget=forms.HiddenInput,
    )

    owner_object: forms.ModelChoiceField = forms.ModelChoiceField(
        label="Owner object",
        required=True,
        queryset=cast("QuerySet[Model]", ContentType.objects.none()),
        help_text="Select an instance of the chosen content type to own this theme.",
    )

    class Meta:
        """Meta configuration for ThemeAdminForm."""

        model = Theme
        fields = (
            "name",
            "slug",
            "description",
            "creator",
            "owner_content_type",
            "owner_object",  # virtual field for UI
            "owner_object_id",  # hidden field kept in sync
        )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the form, hydrating ``owner_object`` queryset from CT.

        The queryset will be:
        - Derived from POSTed ``owner_content_type`` if present, else
        - From the instance's current ``owner_content_type`` if editing.
        """
        super().__init__(*args, **kwargs)
        owner_field = cast(forms.ModelChoiceField, self.fields["owner_object"])

        ct_obj: ContentType | None = None

        # Determine the effective ContentType (POST takes precedence).
        data_ct = self.data.get("owner_content_type")
        if data_ct:
            try:
                ct_obj = ContentType.objects.get(pk=int(data_ct))
            except (ValueError, ContentType.DoesNotExist):
                ct_obj = None
        elif self.instance and self.instance.pk:
            ct_obj = cast(ContentType | None, self.instance.owner_content_type)

        # Set the queryset for owner_object based on the resolved CT.
        if ct_obj is not None:
            model_cls = ct_obj.model_class()
            if model_cls is not None:
                qs: QuerySet[Model] = model_cls._default_manager.all()
                owner_field.queryset = qs

            else:
                # Empty queryset when CT cannot resolve a model class.
                owner_field.queryset = ContentType.objects.none()
        else:
            owner_field.queryset = ContentType.objects.none()

        # Pre-select owner_object when editing an existing instance.
        if (
            self.instance
            and self.instance.pk
            and self.instance.owner_object_id
            and ct_obj is not None
            and ct_obj.model_class() is not None
        ):
            try:
                obj_qs: QuerySet[Model] = owner_field.queryset
                self.initial["owner_object"] = obj_qs.get(
                    pk=self.instance.owner_object_id
                )
                self.initial["owner_object_id"] = self.instance.owner_object_id
            except Exception:
                # If the referenced object no longer exists, leave blank.
                pass

        # Expose the AJAX endpoint on the widget for frontend JS.
        try:
            url = reverse("admin:theming_theme_owner_objects")
            owner_field.widget.attrs["data-owner-objects-url"] = url
        except Exception:
            # In case admin URLs are not yet loaded (e.g., during certain imports).
            pass

    def clean(self) -> dict[str, Any]:
        """
        Ensure ``owner_object_id`` and ``owner_content_type`` are set coherently.

        Returns
        -------
        dict[str, Any]
            The cleaned data.

        Raises
        ------
        ValidationError
            If the selected owner object does not match the selected content type.
        """
        super().clean()

        cleaned: dict[str, Any] = self.cleaned_data

        ct: ContentType | None = cleaned.get("owner_content_type")
        owner_obj: Model | None = cleaned.get("owner_object")

        if ct is None:
            raise ValidationError(
                {"owner_content_type": "Owner content type is required."}
            )
        if owner_obj is None:
            raise ValidationError({"owner_object": "Owner object is required."})

        # Verify that the chosen object belongs to the chosen content type.
        effective_ct = ContentType.objects.get_for_model(
            owner_obj, for_concrete_model=False
        )
        if effective_ct.pk != ct.pk:
            raise ValidationError(
                {
                    "owner_object": "Selected object does not match "
                    "the chosen content type."
                }
            )

        # Synchronize hidden field and instance fields before Model.clean runs.
        cleaned["owner_object_id"] = str(owner_obj.pk)
        self.instance.owner_content_type = ct
        self.instance.owner_object_id = str(owner_obj.pk)

        return cleaned
