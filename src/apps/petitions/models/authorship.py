"""Models for petition authorship."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class PetitionAuthor(models.Model):
    """Link a petition to either a user or an organization."""

    petition = models.ForeignKey(
        "petitions.Petition", on_delete=models.CASCADE, related_name="authorship"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    author = GenericForeignKey("content_type", "object_id")

    class Meta:
        """Meta options for PetitionAuthor model."""

        unique_together = ("petition", "content_type", "object_id")
