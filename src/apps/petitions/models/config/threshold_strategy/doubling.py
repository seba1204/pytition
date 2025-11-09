"""Doubling threshold strategy for petitions."""

from __future__ import annotations

from django.db import models


class DoublingThreshold(models.Model):
    """
    Doubling sequence, e.g., 500 → 1,000 → 2,000 → 4,000 → ...

    Attributes
    ----------
    start_value : int
        Initial threshold value to start from (> 0).
    """

    start_value: models.PositiveIntegerField = models.PositiveIntegerField(
        default=500,
        help_text="First threshold; sequence doubles from there.",
    )

    class Meta:
        """Meta options."""

        verbose_name = "Doubling threshold strategy"

    def describe(self) -> str:
        """Short description of this strategy."""
        return "Doubling sequence starting at start_value"

    def generate_thresholds(self, max_limit: int) -> list[int]:
        """
        Generate ascending thresholds up to `max_limit`.

        Parameters
        ----------
        max_limit : int
            Upper bound for generated thresholds.

        Returns
        -------
        list of int
            Thresholds cropped to `max_limit`.
        """
        if max_limit <= 0 or self.start_value <= 0:
            return []
        out: list[int] = []
        n: int = self.start_value
        while n <= max_limit:
            out.append(n)
            n *= 2
        return out
