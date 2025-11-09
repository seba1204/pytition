"""Webhook notification configuration model."""

from __future__ import annotations

from django.contrib.postgres.fields import ArrayField
from django.core.validators import URLValidator
from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from apps.core.models import BaseSubConfig


class WebhookConfig(BaseSubConfig):
    """
    Configuration for webhook-based notifications.

    Attributes
    ----------
    name : str
        Name of this webhook configuration.
    is_enabled : bool
        Whether this webhook is enabled.
    method : str
        HTTP method to use (e.g., POST, PUT, PATCH).
    url : str
        Target URL for the webhook.
    headers : dict
        Optional HTTP headers to include in the request (can be templated).
    data : dict
        JSON body payload (can be templated).
    timeout_s : float
        Timeout in seconds for the HTTP request.
    verify_tls : bool
        Whether to verify TLS certificates.
    allowed_variables : list of str
        Optional allow-list of variable names for templating.
    """

    name = models.CharField(max_length=200)
    is_enabled = models.BooleanField(default=True)

    method = models.CharField(
        max_length=10,
        choices=[("POST", "POST"), ("PUT", "PUT"), ("PATCH", "PATCH")],
        default="POST",
    )
    url = models.URLField(validators=[URLValidator()])
    # Headers can also be templated strings.
    headers = models.JSONField(
        default=dict, help_text=_lazy("Optional HTTP headers (templated).")
    )
    # Body payload (templated JSON).
    data = models.JSONField(default=dict, help_text=_lazy("Templated JSON body."))

    timeout_s = models.FloatField(default=10.0)
    verify_tls = models.BooleanField(default=True)

    # Optional: restrict usable variables for safety/preview docs
    allowed_variables = ArrayField(
        base_field=models.CharField(max_length=128),
        default=list,
        blank=True,
        help_text=_lazy(
            "Optional allow-list of variable names "
            "(e.g. 'petition.title', 'signature.email')."
        ),
    )
