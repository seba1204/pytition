"""Models for petition authorship."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.core.mixins import HasConfig
from apps.core.model_refs import OPT_IN_CONFIG


class PetitionAuthor(HasConfig, models.Model):
    """Link a petition to either a user or an organization."""

    petition = models.ForeignKey(
        "petitions.Petition", on_delete=models.CASCADE, related_name="authorship"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    author = GenericForeignKey("content_type", "object_id")

    config = {
        "opt_in": OPT_IN_CONFIG,
    }

    class Meta:
        """Meta options for PetitionAuthor model."""

        unique_together = ("petition", "content_type", "object_id")
