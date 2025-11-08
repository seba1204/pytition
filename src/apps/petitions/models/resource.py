"""A model for petition resources (attached files)."""

from __future__ import annotations

from django.db import models

from apps.core.model_refs import PETITION


class PetitionResource(models.Model):
    """A file attached to a petition."""

    petition = models.ForeignKey(
        PETITION, related_name="resources", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to="petition_resources/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Return a string representation of the petition resource."""
        return self.title or self.file.name
