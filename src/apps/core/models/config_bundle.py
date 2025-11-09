"""Configuration bundle model."""

from __future__ import annotations

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from apps.core.mixins import HasOwner


class ConfigBundle(HasOwner, models.Model):
    """
    A reusable configuration bundle that groups multiple sub-configs.

    Notes
    -----
    Scope is modeled via GenericForeignKey so a bundle can be attached to
    different domain models (e.g., Petition or Instance).
    """

    name = models.CharField(
        max_length=200,
        verbose_name=_lazy("Name"),
        help_text=_lazy("A human-readable label for this bundle."),
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_lazy("Is default"),
        help_text=_lazy("Whether this bundle is the default for its owner."),
    )

    scope_ct = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_scope_set",
        verbose_name=_lazy("Scope content type"),
        help_text=_lazy("The content type of the scope of this bundle."),
    )
    scope_id = models.PositiveIntegerField(
        verbose_name=_lazy("Scope object ID"),
        help_text=_lazy("The object ID of the scope of this bundle."),
    )
    scope = GenericForeignKey("scope_ct", "scope_id")

    class Meta:
        """Meta options."""

        verbose_name = _lazy("Configuration bundle")
        verbose_name_plural = _lazy("Configuration bundles")

    def __str__(self) -> str:
        """
        Return human-readable representation.

        Returns
        -------
        str
            The bundle label.
        """
        return f"{self.name} (default={self.is_default})"
