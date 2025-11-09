"""SMTP configuration model."""

from __future__ import annotations

from django.db import models

from apps.core.models import BaseSubConfig


class SMTPConfig(BaseSubConfig):
    """
    SMTP configuration attached to a bundle.

    Attributes
    ----------
    host : str
        SMTP server hostname.
    port : int
        SMTP server port.
    use_tls : bool
        Whether to use STARTTLS.
    username : str | None
        SMTP username.
    password : str | None
        SMTP password (store securely!).
    from_email : str | None
        Default "From" email address.
    """

    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default=587)
    use_tls = models.BooleanField(default=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    from_email = models.EmailField(null=True, blank=True)

    def __str__(self) -> str:
        """
        Return a compact descriptor.

        Returns
        -------
        str
            Display string with host and port.
        """
        return f"SMTP {self.host}:{self.port}"
