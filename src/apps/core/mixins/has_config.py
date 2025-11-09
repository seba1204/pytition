"""Mixin for models with allowed configurations."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from apps.core.model_refs import CONFIG_BUNDLE

if TYPE_CHECKING:
    pass


class HasConfig(models.Model):
    """
    Mixin for models that carry a ConfigBundle.

    Notes
    -----
    - Adds a concrete FK ``config`` to the global bundle model.
    - ``allowed_config`` is a **class-level** contract (not a DB field).
    """

    # Concrete FK on every inheriting model
    bundle_ref = models.ForeignKey(
        CONFIG_BUNDLE,
        # FIXME: [#76] Should not be null, make a good migration script to backfill
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
        verbose_name=_lazy("Configuration bundle"),
        help_text=_lazy("The configuration bundle associated with this object."),
    )

    # Contract: config should be a dictionary of field_name to BaseSubConfig model
    # e.g.
    # {
    #   "mail_config": "notifications.MailConfig",
    #   "smtp_config": "notifications.SmtpConfig"
    # }
    config: ClassVar[dict[str, str]]

    class Meta:
        """Meta options."""

        abstract = True
