"""Configuration models for consents."""

from . import subscribe_method
from .opt_in import OptInConfig

__all__ = [
    "OptInConfig",
    "subscribe_method",
]
