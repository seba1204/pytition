from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy


class ModerationReason(models.Model):
    msg = models.TextField(verbose_name=gettext_lazy("message"))
    visible = models.BooleanField(default=True)

    class Meta:
        db_table = "petition_moderationreason"
        verbose_name = "Moderation reason"
        verbose_name_plural = "Moderation reasons"

    def __str__(self) -> str:
        return self.msg[:64]
