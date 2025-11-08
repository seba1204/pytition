"""A model for petition news items."""

from __future__ import annotations

from django.db import models

from apps.core.model_refs import PETITION


class PetitionNews(models.Model):
    """A news/update item for a petition."""

    petition = models.ForeignKey(
        PETITION, related_name="news", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    date = models.DateField()

    class Meta:
        """Meta options for PetitionNews model."""

        ordering = ["-date", "-id"]

    def __str__(self) -> str:
        """Return a string representation of the petition news item."""
        return f"{self.date} - {self.title}"
