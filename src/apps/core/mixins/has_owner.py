"""HasOwner mixin model."""

from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

from apps.core.model_refs import ORGANIZATION, PYTITION_USER, split_label


def _limit_choices_q(allowed: Sequence[str]) -> Q:
    """
    Build a Q object for limit_choices_to from allowed dotted labels.

    Parameters
    ----------
    allowed : sequence of str
        Dotted labels, e.g. ["accounts.PytitionUser", "organizations.Organization"].

    Returns
    -------
    Q
        OR-ed Q over (app_label, model) pairs.
    """
    q = Q(pk__isnull=True)  # start false
    for dotted in allowed:
        app_label, model = split_label(dotted)
        q |= Q(app_label=app_label, model=model)
    return q


class HasOwner(models.Model):
    """
    Mixin adding a generic 'owner' (user or organization), driven by ALLOWED_OWNER_CT.

    Class Attributes
    ----------------
    ALLOWED_OWNER_CT : tuple[str, ...]
        Dotted labels of allowed owner CTs (e.g. "accounts.PytitionUser").
        **Single source of truth** for this mixin.

    Fields
    ------
    owner_ct : ForeignKey(ContentType)
        Content type of the owner (limited to ALLOWED_OWNER_CT).
    owner_id : PositiveIntegerField
        Primary key of the owner.
    owner : GenericForeignKey
        Virtual relation combining ``owner_ct`` and ``owner_id``.
    """

    # >>> Single source of truth <<<
    ALLOWED_OWNER_CT: ClassVar[tuple[str, ...]] = (
        PYTITION_USER,
        ORGANIZATION,
    )

    owner_ct = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="owner_for_%(app_label)s_%(class)s_set",
        limit_choices_to=_limit_choices_q(
            ALLOWED_OWNER_CT
        ),  # built from the single source of truth
        verbose_name=_lazy("Owner content type"),
        help_text=_lazy("Content type of the owner (restricted by ALLOWED_OWNER_CT)."),
    )
    owner_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_lazy("Owner object ID"),
        help_text=_lazy("Primary key of the owner object."),
    )
    owner = GenericForeignKey("owner_ct", "owner_id")

    class Meta:
        """Meta options."""

        abstract = True

    def clean(self) -> None:
        """
        Validate allowed owner content types and pairing integrity.

        Raises
        ------
        ValidationError
            If (owner_ct, owner_id) is inconsistent or not allowed.
        """
        # Pair integrity
        if (self.owner_ct is None) ^ (self.owner_id is None):
            raise ValidationError(
                _("Both `owner_ct` and `owner_id` must be set, or both must be null.")
            )

        if self.owner_ct is None:
            return  # nothing to validate when empty

        # Check that owner_ct matches ALLOWED_OWNER_CT
        allowed_pairs = {split_label(lbl) for lbl in self.ALLOWED_OWNER_CT}
        app_label = self.owner_ct.app_label.lower()
        model = self.owner_ct.model.lower()
        if (app_label, model) not in allowed_pairs:
            allowed_str = ", ".join(self.ALLOWED_OWNER_CT)
            raise ValidationError(
                _(
                    "Owner content type %(ct)s is not allowed. "
                    "Allowed types are: %(allowed)s."
                )
                % {
                    "ct": f"{self.owner_ct.app_label}.{self.owner_ct.model}",
                    "allowed": allowed_str,
                }
            )

        # Optional existence check (cheap safety)
        if self.owner_id is not None and self.owner is None:
            raise ValidationError(
                _("Owner with id %(id)s does not exist for content type %(ct)s.")
                % {
                    "id": self.owner_id,
                    "ct": f"{self.owner_ct.app_label}.{self.owner_ct.model}",
                }
            )

    def transfer_ownership(self, new_owner: models.Model | None) -> None:
        """
        Transfer ownership to `new_owner`.

        Parameters
        ----------
        new_owner : Model or None
            New owner object, or None to clear ownership.
        """
        if new_owner is None:
            self.owner_ct = None
            self.owner_id = None
        else:
            self.owner_ct = ContentType.objects.get_for_model(new_owner)
            self.owner_id = new_owner.pk
