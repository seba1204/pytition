"""Models for petition threshold configurations."""

from __future__ import annotations

from typing import TypedDict, cast

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

from apps.core.models import BaseSubConfig


class LabeledPoint(TypedDict):
    """Typed dict for labeling points on graphs."""

    x: int
    show_label: bool
    label: str


class ThresholdConfig(BaseSubConfig):
    """
    Configuration holder for petition thresholds.

    Notes
    -----
    - Delegates the logic to a pluggable 'strategy' via ContentType
    - Link to a specific strategy instance using a GenericForeignKey.
    - Exposes helpers to compute thresholds, next target, victory state, and
      lightweight graph annotations (red dots + optional labels).

    Attributes
    ----------
    enabled : bool
        Whether thresholds are active for this petition config.
    victory_limit : int
        Maximum signature count at which the petition is considered a victory.
        Threshold generation will cap at this value.
    stop_on_victory : bool
        If True, petition should be considered closed once `victory_limit` is reached.
    victory_declared_at : datetime or None
        When a victory has been declared (set by app logic).
    strategy_content_type : ContentType
        Content type for the bound strategy model.
    strategy_object_id : int
        Primary key of the bound strategy instance.
    strategy : models.GenericForeignKey
        The attached strategy object implementing threshold generation.
    """

    enabled: models.BooleanField = models.BooleanField(
        default=True,
        help_text=_lazy("Whether thresholds are enabled for this petition."),
        verbose_name=_lazy("Enabled"),
    )
    victory_limit: models.PositiveIntegerField = models.PositiveIntegerField(
        default=10_000,
        help_text=_lazy("Max signatures before declaring victory."),
        verbose_name=_lazy("Victory limit"),
    )
    stop_on_victory: models.BooleanField = models.BooleanField(
        default=True,
        help_text=_lazy("Whether to stop the petition upon reaching victory."),
        verbose_name=_lazy("Stop on victory"),
    )
    victory_declared_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_lazy("Timestamp when victory was declared."),
        verbose_name=_lazy("Victory declared at"),
    )

    # Generic relation to strategy
    strategy_content_type: models.ForeignKey = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name="threshold_configs",
        verbose_name=_lazy("Strategy content type"),
        help_text=_lazy("Content type of the threshold generation strategy."),
    )
    strategy_object_id: models.PositiveIntegerField = models.PositiveIntegerField()
    strategy: GenericForeignKey = GenericForeignKey(
        "strategy_content_type", "strategy_object_id"
    )

    class Meta:
        """Meta options for ThresholdConfig model."""

        verbose_name = "Threshold configuration"
        verbose_name_plural = "Threshold configurations"

    def clean(self) -> None:
        """
        Validate configuration consistency.

        Raises
        ------
        ValidationError
            If fields are inconsistent or invalid.
        """
        super().clean()
        if self.victory_limit <= 0:
            raise ValidationError(
                {"victory_limit": _("Victory limit must be positive.")}
            )
        if self.strategy is None:
            raise ValidationError(
                _("A strategy must be assigned for threshold generation.")
            )

        # Ensure strategy can generate at least one threshold below/equal to the cap.
        thresholds: list[int] = self.thresholds()
        if not thresholds:
            raise ValidationError(
                "Strategy produced no thresholds. Check configuration."
            )
        if thresholds[-1] > self.victory_limit:
            # This can be OK (we crop later), but warn via validation message.
            # Not fatal: we only ensure at least one threshold exists <= cap.
            pass

    # ---------- Core API ----------

    def thresholds(self) -> list[int]:
        """
        Compute all threshold levels (ascending) up to the victory limit.

        Returns
        -------
        list of int
            Sorted ascending thresholds, cropped to `victory_limit`.
        """
        if not self.enabled or self.strategy is None:
            return []
        raw: list[int] = cast(
            list[int], self.strategy.generate_thresholds(self.victory_limit)
        )
        # Normalize: positive, unique, sorted, cropped
        uniq_sorted: list[int] = sorted({n for n in raw if n > 0})
        cropped: list[int] = [n for n in uniq_sorted if n <= self.victory_limit]
        return cropped

    def next_target(self, current_signatures: int) -> int | None:
        """
        Return the next threshold strictly above the current signatures.

        Parameters
        ----------
        current_signatures : int
            Current signature count.

        Returns
        -------
        int or None
            The next target, or None if already at/above the final threshold.
        """
        levels: list[int] = self.thresholds()
        for n in levels:
            if current_signatures < n:
                return n
        return None

    def is_victory(self, current_signatures: int) -> bool:
        """
        Check whether the petition has reached victory.

        Parameters
        ----------
        current_signatures : int
            Current signature count.

        Returns
        -------
        bool
            True if `current_signatures` >= `victory_limit`.
        """
        return bool(current_signatures >= self.victory_limit)

    def mark_victory_if_needed(self, current_signatures: int) -> None:
        """
        Set `victory_declared_at` if victory condition is met.

        Parameters
        ----------
        current_signatures : int
            Current signature count.
        """
        if self.is_victory(current_signatures) and self.victory_declared_at is None:
            self.victory_declared_at = timezone.now()

    # ---------- Graph helpers (for red dots + optional labels) ----------

    def dot_annotations(
        self,
        min_gap: int = 800,
        label_fmt: str = "{n:,}",
    ) -> list[LabeledPoint]:
        """
        Create red-dot annotations with collision-avoiding labels.

        Parameters
        ----------
        min_gap : int, optional
            Minimal spacing between labeled points (in signature units),
            by default 800. Tune per chart width/scale in the frontend.
        label_fmt : str, optional
            Format string for labels, by default '{n:,}'.

        Returns
        -------
        list of dict
            Each item contains `x` (int), `show_label` (bool), `label` (str).
        """
        xs: list[int] = self.thresholds()
        out: list[LabeledPoint] = []
        last_labeled: int | None = None
        for n in xs:
            can_label: bool = last_labeled is None or abs(n - last_labeled) >= min_gap
            out.append(
                LabeledPoint(x=n, show_label=can_label, label=label_fmt.format(n=n))
            )
            if can_label:
                last_labeled = n
        return out

    def strategy_description(self) -> str:
        """
        Human-friendly description of the active strategy.

        Returns
        -------
        str
            Short description string coming from the strategy.
        """
        if self.strategy is None:
            return "No strategy."
        return cast(str, self.strategy.describe())
