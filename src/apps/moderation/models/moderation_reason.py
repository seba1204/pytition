from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _lazy


class ModerationReason(models.Model):
    # Translators: Moderation reason message in the admin interface
    msg = models.TextField(verbose_name=_lazy("message"))
    visible = models.BooleanField(default=True)

    class Meta:
        db_table = "petition_moderationreason"
        # Translators: Moderation reason model name in the admin interface
        verbose_name = _lazy("Moderation reason")
        # Translators: Moderation reason model name (plural) in the admin interface
        verbose_name_plural = _lazy("Moderation reasons")

    def __str__(self) -> str:
        return self.msg[:64]
