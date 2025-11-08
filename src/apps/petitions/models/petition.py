"""Petition model."""

from __future__ import annotations

import html
from typing import TYPE_CHECKING, Any

from colorfield.fields import ColorField  # type: ignore
from django.contrib.auth.hashers import get_hasher
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy
from tinymce import models as tinymce_models  # type: ignore

from apps.core.helpers import sanitize_html
from apps.core.model_refs import ORGANIZATION, PETITION_AUTHOR, PYTITION_USER
from apps.petitions.routes import PetitionsRoute

if TYPE_CHECKING:
    from apps.accounts.models import PytitionUser
    from apps.organizations.models import Organization
    from apps.presets.models import PetitionTemplate


# ----------------------------------- Petition --------------------------------
class Petition(models.Model):
    """Model representing a petition."""

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
    title = models.TextField(verbose_name=_lazy("Title"))
    text = tinymce_models.HTMLField(blank=True)
    tagline = tinymce_models.HTMLField(blank=True)
    target = models.IntegerField(default=500)
    # Owner
    user = models.ForeignKey(
        PYTITION_USER, on_delete=models.CASCADE, null=True, blank=True
    )
    org = models.ForeignKey(
        ORGANIZATION, on_delete=models.CASCADE, null=True, blank=True
    )
    authors = GenericRelation(PETITION_AUTHOR, related_query_name="petition")

    # Colors
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
    illustration = models.ImageField(upload_to="petitions/illustrations/", blank=True)
    has_newsletter = models.BooleanField(default=False)
    newsletter_subscribe_http_data = models.TextField(blank=True)
    newsletter_subscribe_http_mailfield = models.CharField(max_length=100, blank=True)
    newsletter_subscribe_http_url = models.CharField(max_length=1000, blank=True)
    newsletter_subscribe_mail_subject = models.CharField(max_length=1000, blank=True)
    newsletter_subscribe_mail_from = models.CharField(max_length=500, blank=True)
    newsletter_subscribe_mail_to = models.CharField(max_length=500, blank=True)
    newsletter_subscribe_method = models.CharField(
        choices=NEWSLETTER_SUBSCRIBE_METHOD_CHOICES, max_length=4, default=MAIL
    )
    newsletter_subscribe_mail_smtp_host = models.CharField(
        max_length=100, default="localhost", blank=True
    )
    newsletter_subscribe_mail_smtp_port = models.IntegerField(default=25, blank=True)
    newsletter_subscribe_mail_smtp_user = models.CharField(max_length=200, blank=True)
    newsletter_subscribe_mail_smtp_password = models.CharField(
        max_length=200, blank=True
    )
    newsletter_subscribe_mail_smtp_tls = models.BooleanField(default=False)
    newsletter_subscribe_mail_smtp_starttls = models.BooleanField(default=False)
    org_twitter_handle = models.CharField(max_length=20, blank=True)
    published = models.BooleanField(default=False)
    newsletter_text = models.CharField(max_length=1000, blank=True)
    sign_form_footer = models.TextField(blank=True)
    confirmation_email_reply = models.CharField(max_length=100, blank=True)
    salt = models.TextField(blank=True)
    paper_signatures = models.IntegerField(default=0)
    paper_signatures_enabled = models.BooleanField(default=False)
    creation_date = models.DateTimeField(blank=True)
    last_modification_date = models.DateTimeField(blank=True)
    moderated = models.BooleanField(default=False)
    has_email_share_button = models.BooleanField(default=False)
    has_facebook_share_button = models.BooleanField(default=False)
    has_tumblr_share_button = models.BooleanField(default=False)
    has_linkedin_share_button = models.BooleanField(default=False)
    has_twitter_share_button = models.BooleanField(default=False)
    has_mastodon_share_button = models.BooleanField(default=False)
    has_whatsapp_share_button = models.BooleanField(default=False)
    publication_date = models.DateTimeField(blank=True, null=True)
    show_publication_date = models.BooleanField(default=False)

    class Meta:
        """Meta information for Petition model."""

        db_table = "petition_petition"
        # Translators: Petition model verbose name (in the admin interface)
        verbose_name = _lazy("Petition")
        # Translators: Petition model verbose name (in the admin interface)
        verbose_name_plural = _lazy("Petitions")
        ordering = ["-creation_date"]

    @property
    def is_moderated(self) -> bool:
        """Check if the petition is moderated."""
        if self.owner_type == "user":
            # owner is a PytitionUser, which has 'moderated'
            return getattr(self.owner, "moderated", False) or self.moderated
        # owner is an Organization, which does not have 'moderated'
        return self.moderated

    def transfer_to(
        self, user: PytitionUser | None = None, org: Organization | None = None
    ) -> None:
        """Transfer the petition to another owner, either a user or an organization."""
        if user is None and org is None:
            raise ValueError(
                "You should specify either an org or a user when transferring "
                "a petition."
            )
        if user is not None and org is not None:
            raise ValueError(
                "You cannot specify both a user and an org to transfer a petition to."
            )
        if user:
            self.user = user
            self.org = None
        if org:
            self.org = org
            self.user = None
        self.save()

    def prepopulate_from_template(
        self,
        template: PetitionTemplate,
        fields: list[str] | None = None,
        exclude_fields: list[str] | None = None,
    ) -> None:
        """Prepopulate petition fields from a template."""
        if fields is None:
            fields = [
                f.name
                for f in self._meta.fields
                if f.name not in ["id", "title", "salt", "user", "org"]
            ]
        for field in fields:
            if exclude_fields and field in exclude_fields:
                continue
            if hasattr(self, field) and hasattr(template, field):
                template_value = getattr(template, field)
                if template_value is not None and template_value != "":
                    setattr(self, field, template_value)

    def slugify(self) -> None:
        """Generate and save a slug for the petition if none exists."""
        # Slugify the petition title and save it as slugname
        if self.slugmodel_set.count() == 0:
            slugtext = slugify(self.title)
            self.add_slug(slugtext)

    def add_slug(self, slugtext: str) -> None:
        """Add a slug to the petition."""
        # Add a slug correctly
        # lazy import to avoid circular imports
        from apps.petitions.models import SlugModel  # noqa

        with transaction.atomic():
            slugtext = slugify(slugtext)
            # Check if there is another similar slug for the same user/org
            same_slugs = SlugModel.objects.filter(slug=slugtext)
            if len(same_slugs) == 0:
                SlugModel.objects.create(slug=slugtext, petition=self)
            else:
                already_used = False
                for s in same_slugs:
                    if self.owner_type == "org":
                        if (
                            s.petition.owner_type == "org"
                            and self.org == s.petition.org
                        ):
                            already_used = True
                    elif (
                        s.petition.owner_type == "user" and self.user == s.petition.user
                    ):
                        already_used = True
                if already_used:
                    raise ValueError("This slug is already used")
                else:
                    SlugModel.objects.create(slug=slugtext, petition=self)

    def del_slug(self, slug: Any) -> None:
        """Delete a slug from the petition."""
        # Delete a given slug
        # lazy import to avoid circular imports
        from apps.petitions.models import SlugModel  # noqa

        s = SlugModel.objects.filter(slug=slug, petition=self).first()
        if s is not None:
            s.delete()

    @classmethod
    def by_id(cls, id: int) -> Petition | None:
        """Get a Petition by its ID."""
        try:
            return Petition.objects.get(pk=id)
        except Petition.DoesNotExist:
            return None

    def get_signature_number(self, confirmed: bool | None = None) -> int:
        """Get the number of signatures for the petition."""
        qs = self.signature_set.all()
        if confirmed is not None:
            qs = qs.filter(confirmed=confirmed)
        nb_electronic_signatures = qs.count()
        if self.paper_signatures_enabled:
            return nb_electronic_signatures + self.paper_signatures
        else:
            return nb_electronic_signatures

    def already_signed(self, email: str) -> bool:
        """Check if an email has already signed the petition."""
        # lazy import to avoid circular imports
        from apps.signatures.models import Signature  # noqa

        signature_number = (
            Signature.objects.filter(petition=self.id)
            .filter(confirmed=True)
            .filter(email=email)
            .count()
        )
        return signature_number > 0

    @property
    def signature_progress(self) -> int:
        """
        Compute signature progress towards target in percent.

        Returns
        -------
        int
            A clamped percentage between 0 and 100.
        """
        try:
            pct = int(round((self.signature_number * 100) / max(1, self.target)))
        except Exception:
            pct = 0
        return max(0, min(100, pct))

    def confirm_signature(self, conf_hash: str) -> str | None:
        """Confirm a signature given its confirmation hash."""
        # lazy import to avoid circular imports
        from apps.signatures.models import Signature  # noqa

        signature = Signature.objects.filter(petition=self.id).get(
            confirmation_hash=conf_hash
        )
        if signature:
            # Now confirm the signature corresponding to this hash
            signature.confirm()
            signature.save()
            return _("Thank you for confirming your signature!")
        else:
            return None

    def publish(self) -> None:
        """Publish the petition."""
        self.published = True
        self.publication_date = timezone.now()
        self.save()

    def unpublish(self) -> None:
        """Unpublish the petition."""
        self.published = False
        self.publication_date = None
        self.save()

    @property
    def to_json(self) -> dict[str, Any]:
        """Get a JSON representation of the petition."""
        return {
            "title": self.title,
            "signatures": self.get_signature_number(True),
            "text": self.text,
            "target": self.target,
            "description": self.twitter_description,
            "image": self.twitter_image,
            "org_twitter_handle": self.org_twitter_handle,
            "has_newsletter": self.has_newsletter,
            "creator": self.owner_name,
        }

    @property
    def owner_type(self) -> str:
        """Get the type of the petition owner."""
        if self.org:
            return "org"
        else:
            return "user"

    @property
    def owner_name(self) -> str:
        """Get the name of the petition owner."""
        return str(self.owner)

    @property
    def owner_username(self) -> str:
        """Get the username or slugname of the petition owner."""
        if self.owner_type == "org":
            if self.org is not None:
                return self.org.slugname
            else:
                return ""
        else:
            return self.user.username if self.user is not None else ""

    @property
    def owner(self) -> Organization | PytitionUser:
        """Get the owner of the petition."""
        if self.org is not None:
            return self.org
        elif self.user is not None:
            return self.user
        else:
            raise ValueError("Petition has no owner (neither org nor user is set)")

    @property
    def signature_number(self) -> int:
        """Get the number of confirmed signatures for the petition."""
        return self.get_signature_number(True)

    @property
    def raw_twitter_description(self) -> str:
        """Get the raw twitter description without HTML tags."""
        return html.unescape(
            mark_safe(strip_tags(sanitize_html(self.twitter_description)))
        )

    @property
    def raw_text(self) -> str:
        """Get the raw text of the petition without HTML tags."""
        return html.unescape(mark_safe(strip_tags(sanitize_html(self.text))))

    def __str__(self) -> str:
        """String representation of the petition."""
        return self.title

    def __repr__(self) -> str:
        """Official string representation of the petition."""
        return self.title

    def is_allowed_to_edit(self, user: PytitionUser) -> bool:
        """Check if a user is allowed to edit this petition."""
        # lazy import to avoid circular imports
        from apps.accounts.models import Permission  # noqa

        if self.owner_type == "user":
            # The user is the owner of the petition
            return self.user == user
        # The petition is owned by an organization
        try:
            perm = Permission.objects.get(organization=self.org, user=user)
        except Permission.DoesNotExist:
            # No such permission, denied
            return False
        return perm.can_modify_petitions

    @property
    def url(self) -> str:
        """Get the URL of the petition."""
        slugs = self.slugmodel_set.all()
        if len(slugs) == 0:
            # If there is no slug, ugly url
            return reverse(PetitionsRoute.DETAIL, kwargs={"petition_id": self.id})
        elif self.owner_type == "org":
            #  This petition is owned by an Organization
            if self.org is not None:
                return reverse(PetitionsRoute.DETAIL, kwargs={"petition_id": self.id})
            else:
                raise ValueError(_("This petition is missing an organization owner."))
        elif self.owner_type == "user":
            # This petition is owned by a PytitionUser
            if self.user is not None:
                return reverse(PetitionsRoute.DETAIL, kwargs={"petition_id": self.id})
            else:
                raise ValueError(_("This petition is missing a user owner."))
        else:
            # This is a BUG!
            raise ValueError(_("This petition is buggy. Sorry about that!"))

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save the petition, ensuring integrity constraints."""
        if self.org is None and self.user is None:
            raise Exception("You need to provide a user or org as owner")
        elif self.org is not None and self.user is not None:
            raise Exception("A petition can have only one owner")
        elif not self.salt:
            hasher = get_hasher()
            salt: bytes | str = hasher.salt()
            self.salt = salt.decode("utf-8") if isinstance(salt, bytes) else str(salt)
        self.last_modification_date = timezone.now()
        super().save(*args, **kwargs)

    def moderate(self, do_moderate: bool = True) -> None:
        """Set the moderated status of the petition."""
        self.moderated = do_moderate
        self.save()

    @property
    def has_any_share_button(self) -> bool:
        """Check if any share button is enabled for the petition."""
        return (
            self.has_email_share_button
            or self.has_facebook_share_button
            or self.has_tumblr_share_button
            or self.has_linkedin_share_button
            or self.has_twitter_share_button
            or self.has_mastodon_share_button
            or self.has_whatsapp_share_button
        )
