"""SMTP configuration model."""

from __future__ import annotations

from django.db import models

from apps.core.models import BaseSubConfig


class MailConfig(BaseSubConfig):
    """
    Mail notification configuration attached to a bundle.

    Attributes
    ----------
    subject_prefix : str
        Prefix for the email subject line.
    reply_to : str | None
        Reply-To email address.
    template : str
        Email template content.
    use_html : bool
        Whether to send the email as HTML.
    recipient_email : str
        Default recipient email address.
    sender_name : str
        Name of the email sender.
    sender_email : str
        Email address of the sender.
    """

    subject_prefix = models.CharField(max_length=100, default="[Notification]")
    reply_to = models.EmailField(null=True, blank=True)
    template = models.TextField()
    use_html = models.BooleanField(default=True)
    recipient_email = models.EmailField()
    sender_name = models.CharField(max_length=100, default="No Reply")
    sender_email = models.EmailField()
