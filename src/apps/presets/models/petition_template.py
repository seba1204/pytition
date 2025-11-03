from __future__ import annotations

from typing import Any

from colorfield.fields import ColorField  # type: ignore
from django.db import models
from django.utils.translation import gettext_lazy
from tinymce import models as tinymce_models  # type: ignore

from apps.core.model_refs import ORGANIZATION, PYTITION_USER


class PetitionTemplate(models.Model):
    NO = "no gradient"
    RIGHT = "to right"
    BOTTOM = "to bottom"
    BOTTOM_RIGHT = "to bottom right"
    BOTTOM_LEFT = "to bottom left"

    LINEAR_GRADIENT_CHOICES = (
        (NO, "no gradient"),
        (RIGHT, "to right"),
        (BOTTOM, "to bottom"),
        (BOTTOM_RIGHT, "to bottom right"),
        (BOTTOM_LEFT, "to bottom left"),
    )

    MAIL = "MAIL"
    POST = "POST"
    GET = "GET"

    NEWSLETTER_SUBSCRIBE_METHOD_CHOICES = ((MAIL, "MAIL"), (POST, "POST"), (GET, "GET"))

    # Description
    # Translators: Petition template name field in models (admin interface)
    name = models.CharField(max_length=50, verbose_name=gettext_lazy("Name"))
    text = tinymce_models.HTMLField(blank=True)
    side_text = tinymce_models.HTMLField(blank=True)
    target = models.IntegerField(blank=True, null=True)
    # Owner
    user = models.ForeignKey(
        PYTITION_USER, on_delete=models.CASCADE, null=True, blank=True
    )
    org = models.ForeignKey(
        ORGANIZATION, on_delete=models.CASCADE, null=True, blank=True
    )
    # Fancy colors
    linear_gradient_direction = models.CharField(
        choices=LINEAR_GRADIENT_CHOICES, max_length=15, default=NO, blank=True
    )
    gradient_from = ColorField(blank=True)
    gradient_to = ColorField(blank=True)
    bgcolor = ColorField(blank=True)
    footer_text = tinymce_models.HTMLField(blank=True)
    footer_links = tinymce_models.HTMLField(blank=True)
    twitter_description = models.CharField(max_length=200, blank=True)
    twitter_image = models.CharField(max_length=500, blank=True)
    has_newsletter = models.BooleanField(default=False)
    newsletter_subscribe_http_data = models.TextField(blank=True)
    newsletter_subscribe_http_mailfield = models.CharField(max_length=100, blank=True)
    newsletter_subscribe_http_url = models.CharField(max_length=1000, blank=True)
    newsletter_subscribe_mail_subject = models.CharField(max_length=1000, blank=True)
    newsletter_subscribe_mail_from = models.EmailField(max_length=500, blank=True)
    newsletter_subscribe_mail_to = models.EmailField(max_length=500, blank=True)
    newsletter_subscribe_method = models.CharField(
        choices=NEWSLETTER_SUBSCRIBE_METHOD_CHOICES, max_length=4, default=MAIL
    )
    newsletter_subscribe_mail_smtp_host = models.CharField(
        max_length=100, default="localhost", blank=True
    )
    newsletter_subscribe_mail_smtp_port = models.IntegerField(default=25)
    newsletter_subscribe_mail_smtp_user = models.CharField(max_length=200, blank=True)
    newsletter_subscribe_mail_smtp_password = models.CharField(
        max_length=200, blank=True
    )
    newsletter_subscribe_mail_smtp_tls = models.BooleanField(default=False)
    newsletter_subscribe_mail_smtp_starttls = models.BooleanField(default=False)
    org_twitter_handle = models.CharField(max_length=20, blank=True)
    newsletter_text = models.CharField(max_length=1000, blank=True)
    sign_form_footer = models.TextField(blank=True)
    confirmation_email_reply = models.EmailField(max_length=100, blank=True)
    use_custom_email_settings = models.BooleanField(default=False)
    has_email_share_button = models.BooleanField(default=False)
    has_facebook_share_button = models.BooleanField(default=False)
    has_tumblr_share_button = models.BooleanField(default=False)
    has_linkedin_share_button = models.BooleanField(default=False)
    has_twitter_share_button = models.BooleanField(default=False)
    has_mastodon_share_button = models.BooleanField(default=False)
    has_whatsapp_share_button = models.BooleanField(default=False)
    paper_signatures_enabled = models.BooleanField(default=False)

    class Meta:
        db_table = "petition_petitiontemplate"
        # Translators: Petition template model name in models (admin interface)
        verbose_name = gettext_lazy("Petition template")
        # Translators: Petition template model name plural in models (admin interface)
        verbose_name_plural = gettext_lazy("Petition Templates")

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    @property
    def owner_type(self) -> str:
        if self.org:
            return "org"
        else:
            return "user"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.org is None and self.user is None:
            raise Exception("You need to provide a user or org as owner")
        elif self.org is not None and self.user is not None:
            raise Exception("A petition can have only one owner")
        else:
            super().save(*args, **kwargs)
