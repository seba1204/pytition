"""Doubling threshold strategy for petitions."""

from __future__ import annotations

from typing import Any

from django.db import models

from apps.consents.mixins import HasSubscribe
from apps.core.mixins import HasConfig
from apps.core.model_refs import WEBHOOK_CONFIG


class WebhookSubscribeMethod(HasSubscribe, HasConfig, models.Model):
    """
    Subscribe method using webhooks.

    Attributes
    ----------
    webhook_config : ForeignKey
        Configuration for the webhook.
    """

    config = {
        "webhook": WEBHOOK_CONFIG,
    }

    class Meta:
        """Meta options."""

        verbose_name = "Webhook subscribe method"

    def subscribe(self, user: Any, **kwargs: Any) -> None:
        """
        Add the given user to the list of subscribers.

        Parameters
        ----------
        user : Any
            The user object subscribing to the newsletter.
        **kwargs : Any
            Additional optional arguments, e.g., preferences or tags.
        """
        # Placeholder implementation; actual email sending logic would go here.
        pass
