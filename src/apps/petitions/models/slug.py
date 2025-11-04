"""Models for petition slugs (permalinks)."""
from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from apps.core.model_refs import PETITION


# --------------------------------- SlugModel ---------------------------------
class SlugModel(models.Model):
    """Model for petition slugs (permalinks)."""

    slug = models.SlugField(max_length=200)
    petition = models.ForeignKey(PETITION, on_delete=models.CASCADE)

    class Meta:
        """Meta information for the SlugModel."""

        db_table = "petition_slugmodel"
        # Translators: Slug model verbose name (in the admin interface)
        verbose_name = gettext_lazy("Slug")
        # Translators: Slug model verbose name (in the admin interface)
        verbose_name_plural = gettext_lazy("Slugs")

    def clean(self, *args: Any, **kwargs: Any) -> None:
        """Ensure that the slug is not empty."""
        if self.slug == "" or self.slug is None:
            raise ValidationError(
                _("A permalink cannot be empty. Please enter something."),
                code="invalid",
            )
        super().clean(*args, **kwargs)

    def __str__(self) -> str:
        return self.slug

    def __repr__(self) -> str:
        return self.slug
