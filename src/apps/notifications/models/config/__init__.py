"""Configuration models for notifications."""

from .mail import MailConfig
from .smtp import SMTPConfig

__all__ = [
    "MailConfig",
    "SMTPConfig",
]
