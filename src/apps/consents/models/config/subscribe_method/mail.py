"""Doubling threshold strategy for petitions."""

from __future__ import annotations

from typing import Any

from django.db import models

from apps.consents.mixins import HasSubscribe
from apps.core.mixins import HasConfig
from apps.core.model_refs import MAIL_TEMPLATE_CONFIG, SMTP_CONFIG


class MailSubscribeMethod(HasSubscribe, HasConfig, models.Model):
    """
    Subscribe method using email.

    Attributes
    ----------
    mail_config : ForeignKey
        Configuration for the mail.

    Notes
    -----
    Mail subscription method consists of sending an email to a newsletter
    management system (e.g., Sympa, Mailman, etc.) to add the user to a
    mailing list.
    """

    config = {
        "mail": MAIL_TEMPLATE_CONFIG,
        "smtp": SMTP_CONFIG,
    }

    class Meta:
        """Meta options."""

        verbose_name = "Mail subscribe method"

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
