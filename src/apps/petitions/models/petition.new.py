"""Petition model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _lazy
from tinymce import models as tinymce_models  # type: ignore

from apps.core.mixins import HasConfig, HasOwner
from apps.core.model_refs import (
    PETITION_AUTHOR,
    SHARING_CONFIG,
    SMTP_CONFIG,
    THRESHOLD_CONFIG,
)

if TYPE_CHECKING:
    pass


# ----------------------------------- Petition --------------------------------
class Petition(HasOwner, HasConfig, models.Model):
    """Model representing a petition."""

    class Config:
        """Configuration for HasConfig mixin."""

        verbose_name = "Petition configuration"

        threshold = {
            "config": THRESHOLD_CONFIG,
            "verbose_name": "Threshold configuration",
            "help_text": "Signature number thresholds for this petition.",
        }

        mails = {
            "config": SMTP_CONFIG,
            "verbose_name": "SMTP configuration",
            "help_text": "SMTP config for sending emails related to this petition.",
        }

        sharing = {
            "config": SHARING_CONFIG,
            "verbose_name": "Sharing configuration",
            "help_text": "Configuration for sharing options of this petition.",
        }

        # all these settings will be auto discovered in the settings page
        # the setting view is in charge of "manually" adding the opt-in config
        # according to the authors and current logged in user
        # (show only opt-in settings that the user can actually edit)
        # To do this, the trick is to set the author as the setting owner, and not the
        # current user.

    state = models.CharField(
        max_length=10,
        choices=(
            ("draft", "Draft"),
            ("published", "Published"),
            ("moderated", "Moderated"),
            ("closed", "Closed"),
            ("won", "Won"),
        ),
        default="draft",
    )
    # Description
    title = models.TextField(verbose_name=_lazy("Title"))
    text = tinymce_models.HTMLField(blank=True)
    tagline = tinymce_models.TextField(blank=True)
    target = models.IntegerField(default=500)
    authors = GenericRelation(PETITION_AUTHOR, related_query_name="petition")
    illustration = models.ImageField(upload_to="petitions/illustrations/", blank=True)
    published = models.BooleanField(default=False)
    salt = models.TextField(blank=True)
    creation_date = models.DateTimeField(blank=True)
    last_modification_date = models.DateTimeField(blank=True)
    publication_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Meta information for Petition model."""

        db_table = "petition_petition"
        # Translators: Petition model verbose name (in the admin interface)
        verbose_name = _lazy("Petition")
        # Translators: Petition model verbose name (in the admin interface)
        verbose_name_plural = _lazy("Petitions")
        ordering = ["-creation_date"]
