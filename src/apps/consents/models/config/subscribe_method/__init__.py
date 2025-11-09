"""Subscribe method configuration models for consents."""

from .mail import MailSubscribeMethod
from .webhook import WebhookSubscribeMethod

__all__ = [
    "MailSubscribeMethod",
    "WebhookSubscribeMethod",
]
