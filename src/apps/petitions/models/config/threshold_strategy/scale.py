"""Scale-based threshold strategy for petitions."""

from __future__ import annotations

from collections.abc import Sequence

from django.core.exceptions import ValidationError
from django.db import models


def default_multipliers() -> list[float]:
    """
    Return the default list of threshold multipliers.

    Returns
    -------
    list of float
        Default ordered positive multipliers, e.g. [1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10].
    """
    return [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]


class ScaleThreshold(models.Model):
    """
    Scale-based thresholds like [1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10] × 10^k.

    Notes
    -----
    - `unit` scales the multipliers to meaningful signature counts.
      For example, multipliers=[1,1.5,2,...], unit=100 gives: 100, 150, 200, ...
    - By default, this matches the classic engineering-like scale.

    Attributes
    ----------
    multipliers : JSON
        Ordered positive floats used as the base sequence for each decade.
    unit : int
        Base unit multiplied by each multiplier.
    k_min : int
        Minimal decade exponent to start from (10^k_min).
    """

    multipliers: models.JSONField = models.JSONField(
        default=default_multipliers,
        help_text="Ordered positive floats, e.g. [1,1.5,2,2.5,3,4,5,6,8,10].",
    )
    unit: models.PositiveIntegerField = models.PositiveIntegerField(
        default=100,
        help_text="Base unit multiplied by each multiplier.",
    )
    k_min: models.IntegerField = models.IntegerField(
        default=0,
        help_text="Start decade exponent (10^k) to generate from.",
    )

    class Meta:
        """Meta options."""

        verbose_name = "Scale threshold strategy"

    def describe(self) -> str:
        """Short description of this strategy."""
        return "Scale: multipliers × 10^k"

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
        if max_limit <= 0:
            return []
        # Ensure valid multipliers
        try:
            multipliers: Sequence[float] = tuple(float(m) for m in self.multipliers)
        except Exception as err:
            raise ValidationError(
                {"multipliers": "Must be a JSON array of numbers."}
            ) from err
        if any(m <= 0 for m in multipliers):
            raise ValidationError({"multipliers": "All multipliers must be > 0."})
        if self.unit <= 0:
            raise ValidationError({"unit": "Unit must be > 0."})

        out: list[int] = []
        k: int = self.k_min
        # Iterate decades until we surpass the cap by an entire decade.
        while True:
            decade: float = 10.0**k
            produced_any: bool = False
            for m in multipliers:
                n_float: float = m * decade * float(self.unit)
                n: int = int(round(n_float))
                if n <= 0:
                    continue
                if n > max_limit:
                    # Stop adding for this decade; keep loop to allow exit condition.
                    continue
                out.append(n)
                produced_any = True
            # If the smallest multiplier for next decade already exceeds the cap
            # and nothing was produced this round, break.
            smallest_next: float = (
                float(multipliers[0]) * (10.0 ** (k + 1)) * float(self.unit)
            )
            if smallest_next > max_limit and not produced_any:
                break
            k += 1
        # Deduplicate + sort
        return sorted(set(out))
