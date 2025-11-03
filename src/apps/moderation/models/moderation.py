from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from apps.core.model_refs import MODERATION_REASON, PETITION


# FIXME: According to the PytitionUser model, user can be moderated too.
# cf. ticket #60.
class Moderation(models.Model):
    """Model representing a moderation action taken on a petition."""

    petition = models.ForeignKey(PETITION, on_delete=models.CASCADE)
    reason = models.ForeignKey(
        MODERATION_REASON, blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        db_table = "petition_moderation"
        # Translators: Moderation model name in the admin interface
        verbose_name = _lazy("Moderation")
