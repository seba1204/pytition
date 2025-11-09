"""Opt-in consent configuration model."""

from __future__ import annotations

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

from apps.core.models import BaseSubConfig


class OptInConfig(BaseSubConfig):
    """
    Configuration for opt-in consent methods.

    Attributes
    ----------
    consent_text : str
        Text presented to users for consent.
    subscribe_method : int
        Method used for subscribing (e.g., email protocol).
    is_enabled : bool
        Whether this opt-in configuration is active.
    method_content_type : ForeignKey(ContentType)
        Content type of the consent method.
    method_object_id : int
        Primary key of the consent method instance.
    consent_method : GenericForeignKey
        The attached consent method object.
    """

    consent_text = models.CharField(max_length=255)
    subscribe_method = models.PositiveIntegerField(default=587)
    is_enabled = models.BooleanField(default=True)

    # Generic relation to method
    method_content_type: models.ForeignKey = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name="opt_in_configs",
        verbose_name=_lazy("Consent method content type"),
        help_text=_lazy("Content type of the consent method."),
    )
    method_object_id: models.PositiveIntegerField = models.PositiveIntegerField()
    consent_method: GenericForeignKey = GenericForeignKey(
        "method_content_type", "method_object_id"
    )

    def __str__(self) -> str:
        """String representation of the OptInConfig."""
        return _("Opt-in config: %s") % self.consent_text
