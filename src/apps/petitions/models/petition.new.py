"""Petition model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _lazy
from tinymce import models as tinymce_models  # type: ignore

from apps.core.mixins import HasConfig, HasOwner
from apps.core.model_refs import (
    MAIL_CONFIG,
    PETITION_AUTHOR,
    SHARING_CONFIG,
    SMTP_CONFIG,
)

if TYPE_CHECKING:
    pass


# ----------------------------------- Petition --------------------------------
class Petition(HasOwner, HasConfig, models.Model):
    """Model representing a petition."""

    config = {
        "confirmation_mail": MAIL_CONFIG,
        "smtp": SMTP_CONFIG,
        "sharing": SHARING_CONFIG,
    }
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
