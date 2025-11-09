"""Fixed percentage threshold strategy for petitions."""

from __future__ import annotations

from django.db import models


class FixedPercentThreshold(models.Model):
    """
    Fixed percentage steps of the victory limit (rounded).

    Examples
    --------
    With `step_percent=10` and victory_limit=10_000:
    thresholds = [1_000, 2_000, ..., 10_000]

    Attributes
    ----------
    step_percent : int
        Percentage step size in [1, 100]. For 5% steps, set 5.
    round_to : int
        Round each threshold to the nearest multiple of `round_to` (>= 1).
        Use 1 for no rounding beyond integer conversion.
    include_zero : bool
        If True, a 0% level is ignored anyway (no threshold at 0); kept for clarity.
    """

    step_percent: models.PositiveIntegerField = models.PositiveIntegerField(
        default=10,
        help_text="Percentage step in [1..100], e.g. 5 or 10.",
    )
    round_to: models.PositiveIntegerField = models.PositiveIntegerField(
        default=100,
        help_text="Round each level to nearest multiple, e.g. 100.",
    )
    include_zero: models.BooleanField = models.BooleanField(
        default=False,
        help_text="No effect on output; kept for readability.",
    )

    class Meta:
        """Meta options."""

        verbose_name = "Fixed percent threshold strategy"

    def describe(self) -> str:
        """Short description of this strategy."""
        return f"Fixed {self.step_percent}% steps of victory_limit"

    def generate_thresholds(self, max_limit: int) -> list[int]:
        """
        Generate ascending thresholds up to `max_limit`.

        Parameters
        ----------
        max_limit : int
            Upper bound (typically the petition's victory limit).

        Returns
        -------
        list of int
            Thresholds cropped to `max_limit`.
        """
        step: int = int(self.step_percent)
        MAX_PERCENT: int = 100
        if max_limit <= 0 or not (1 <= step <= MAX_PERCENT) or self.round_to <= 0:
            return []
        out: list[int] = []
        pct: int = step
        while pct <= MAX_PERCENT:
            raw: float = (pct / float(MAX_PERCENT)) * float(max_limit)
            # Round to nearest multiple of `round_to`
            rounded: int = int(round(raw / self.round_to) * self.round_to)
            if 0 < rounded <= max_limit:
                out.append(rounded)
            pct += step
        return sorted(set(out))
