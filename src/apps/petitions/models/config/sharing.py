"""Sharing configuration for petitions."""

from __future__ import annotations

from django.db import models

from apps.core.models import BaseSubConfig


class ShareMethod(models.Model):
    """
    Global registry of share methods (extensible).

    Attributes
    ----------
    code : str
        Stable unique slug used by frontend/router (e.g., "copy", "email", "twitter").
    label : str
        Human-readable label (i18n handled in UI).
    is_builtin : bool
        Whether this method ships by default (for seeding and safety).
    default_position : int
        Suggested default ordering when added to a petition.
    default_data : dict[str, Any]
        Default provider-specific payload (e.g., {"subject": "..."} for email).
    schema : dict[str, Any]
        Optional JSON Schema used by admin to validate `data` overrides.
    icon : str
        Optional icon key (frontend lookup).
    """

    code = models.SlugField(max_length=50, unique=True)
    label = models.CharField(max_length=100)
    is_builtin = models.BooleanField(default=True)
    default_position = models.PositiveIntegerField(default=0)
    default_data = models.JSONField(default=dict, blank=True)
    schema = models.JSONField(default=dict, blank=True)
    icon = models.CharField(max_length=100, blank=True)

    class Meta:
        """Meta options."""

        ordering = ["default_position", "code"]

    def __str__(self) -> str:
        """String representation."""
        return self.code


class SharingConfig(BaseSubConfig):
    """
    Sharing configuration attached to a petition.

    Attributes
    ----------
    methods : ManyToManyField
        Share methods enabled for this petition.
    """

    methods = models.ManyToManyField(
        ShareMethod,
        related_name="sharing_configs",
        blank=True,
    )

    class Meta:
        """Meta options."""

        verbose_name = "Sharing configuration"
