from __future__ import annotations

import html
from typing import TYPE_CHECKING, Any

from colorfield.fields import ColorField  # type: ignore
from django.conf import settings
from django.contrib.auth.hashers import get_hasher
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from tinymce import models as tinymce_models  # type: ignore

from apps.core.helpers import sanitize_html
from apps.core.model_refs import ORGANIZATION, PETITION_TEMPLATE, PYTITION_USER
from apps.petitions.routes import PetitionsRoute

if TYPE_CHECKING:
    from apps.organizations.models import Organization
    from apps.presets.models import PetitionTemplate


class PytitionUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pytitionuser"
    )
    invitations: models.ManyToManyField = models.ManyToManyField(
        ORGANIZATION, related_name="invited", blank=True
    )
    default_template = models.ForeignKey(
        PETITION_TEMPLATE,
        blank=True,
        null=True,
        related_name="+",
        verbose_name=gettext_lazy("Default petition template"),
        to_field="id",
        on_delete=models.SET_NULL,
    )
    moderated = models.BooleanField(default=False)

    def drop(self) -> None:
        with transaction.atomic():
            orgs = list(self.organization_set.all())
            petitions = list(self.petition_set.all())
            templates = list(self.petitiontemplate_set.all())
            self.delete()
            for org in orgs:
                if org.members.count() == 0:
                    org.delete()
            for petition in petitions:
                petition.delete()
            for template in templates:
                template.delete()

    def moderate(self, do_moderate: bool = True) -> None:
        self.moderated = do_moderate
        self.save()

    @property
    def is_authenticated(self) -> bool:
        return self.user.is_authenticated

    @property
    def name(self) -> str:
        return self.username

    @property
    def username(self) -> str:
        return self.user.username if self.user is not None else ""

    @property
    def get_full_name(self) -> str:
        return self.user.get_full_name()

    @property
    def fullname(self) -> str:
        return self.get_full_name

    @property
    def kind(self) -> str:
        return "user"

    def __str__(self) -> str:
        if self.get_full_name != "":
            return self.get_full_name
        else:
            return self.username

    def __repr__(self) -> str:
        if self.get_full_name != "":
            return self.get_full_name
        else:
            return self.username


# ----------------------------------- Petition --------------------------------
class Petition(models.Model):
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
    title = models.TextField(verbose_name=gettext_lazy("Title"))
    text = tinymce_models.HTMLField(blank=True)
    side_text = tinymce_models.HTMLField(blank=True)
    target = models.IntegerField(default=500)
    # Owner
    user = models.ForeignKey(
        PytitionUser, on_delete=models.CASCADE, null=True, blank=True
    )
    org = models.ForeignKey(
        ORGANIZATION, on_delete=models.CASCADE, null=True, blank=True
    )
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

    @property
    def is_moderated(self) -> bool:
        if self.owner_type == "user":
            # owner is a PytitionUser, which has 'moderated'
            return getattr(self.owner, "moderated", False) or self.moderated
        # owner is an Organization, which does not have 'moderated'
        return self.moderated

    def transfer_to(
        self, user: PytitionUser | None = None, org: Organization | None = None
    ) -> None:
        if user is None and org is None:
            raise ValueError(
                "You should specify either an org or a user when transferring "
                "a petition"
            )
        if user is not None and org is not None:
            raise ValueError(
                "You cannot specify both a user and an org to transfer a petition to"
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
        # Slugify the petition title and save it as slugname
        if self.slugmodel_set.count() == 0:
            slugtext = slugify(self.title)
            self.add_slug(slugtext)

    def add_slug(self, slugtext: str) -> None:
        # Add a slug correctly
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
        # Delete a given slug
        s = SlugModel.objects.filter(slug=slug, petition=self).first()
        if s is not None:
            s.delete()

    @classmethod
    def by_id(cls, id: int) -> Petition | None:
        try:
            return Petition.objects.get(pk=id)
        except Petition.DoesNotExist:
            return None

    def get_signature_number(self, confirmed: bool | None = None) -> int:
        qs = self.signature_set.all()
        if confirmed is not None:
            qs = qs.filter(confirmed=confirmed)
        nb_electronic_signatures = qs.count()
        if self.paper_signatures_enabled:
            return nb_electronic_signatures + self.paper_signatures
        else:
            return nb_electronic_signatures

    def already_signed(self, email: str) -> bool:
        from apps.signatures.models import Signature  # noqa

        signature_number = (
            Signature.objects.filter(petition=self.id)
            .filter(confirmed=True)
            .filter(email=email)
            .count()
        )
        return signature_number > 0

    def confirm_signature(self, conf_hash: str) -> str | None:
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
        self.published = True
        self.publication_date = timezone.now()
        self.save()

    def unpublish(self) -> None:
        self.published = False
        self.publication_date = None
        self.save()

    @property
    def to_json(self) -> dict[str, Any]:
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
        if self.org:
            return "org"
        else:
            return "user"

    @property
    def owner_name(self) -> str:
        return str(self.owner)

    @property
    def owner_username(self) -> str:
        if self.owner_type == "org":
            if self.org is not None:
                return self.org.slugname
            else:
                return ""
        else:
            return self.user.username if self.user is not None else ""

    @property
    def owner(self) -> Organization | PytitionUser:
        if self.org is not None:
            return self.org
        elif self.user is not None:
            return self.user
        else:
            raise ValueError("Petition has no owner (neither org nor user is set)")

    @property
    def signature_number(self) -> int:
        return self.get_signature_number(True)

    @property
    def raw_twitter_description(self) -> str:
        return html.unescape(
            mark_safe(strip_tags(sanitize_html(self.twitter_description)))
        )

    @property
    def raw_text(self) -> str:
        return html.unescape(mark_safe(strip_tags(sanitize_html(self.text))))

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return self.title

    def is_allowed_to_edit(self, user: PytitionUser) -> bool:
        """Check if a user is allowed to edit this petition."""
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
        slugs = self.slugmodel_set.all()
        if len(slugs) == 0:
            # If there is no slug, ugly url
            return reverse(PetitionsRoute.DETAIL, kwargs={"petition_id": self.id})
        elif self.owner_type == "org":
            #  This petition is owned by an Organization
            if self.org is not None:
                return reverse(
                    "slug_show_petition",
                    kwargs={"orgslugname": self.org.slugname, "petitionname": slugs[0]},
                )
            else:
                raise ValueError(_("This petition is missing an organization owner."))
        elif self.owner_type == "user":
            # This petition is owned by a PytitionUser
            if self.user is not None:
                return reverse(
                    "slug_show_petition",
                    kwargs={"username": self.user.username, "petitionname": slugs[0]},
                )
            else:
                raise ValueError(_("This petition is missing a user owner."))
        else:
            # This is a BUG!
            raise ValueError(_("This petition is buggy. Sorry about that!"))

    def save(self, *args: Any, **kwargs: Any) -> None:
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
        self.moderated = do_moderate
        self.save()

    @property
    def has_any_share_button(self) -> bool:
        return (
            self.has_email_share_button
            or self.has_facebook_share_button
            or self.has_tumblr_share_button
            or self.has_linkedin_share_button
            or self.has_twitter_share_button
            or self.has_mastodon_share_button
            or self.has_whatsapp_share_button
        )


# --------------------------------- SlugModel ---------------------------------
class SlugModel(models.Model):
    slug = models.SlugField(max_length=200)
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE)

    def clean(self, *args: Any, **kwargs: Any) -> None:
        if self.slug == "" or self.slug is None:
            raise ValidationError(
                _("A permalink cannot be empty. Please enter something."),
                code="invalid",
            )
        super().clean(*args, **kwargs)

    def __str__(self) -> str:
        return self.slug

    def __repr__(self) -> str:
        return self.slug


# ------------------------------------ Permission -----------------------------
class Permission(models.Model):
    organization = models.ForeignKey(
        ORGANIZATION,
        on_delete=models.CASCADE,
        verbose_name=gettext_lazy("Organization related to these permissions"),
    )
    user = models.ForeignKey(
        PYTITION_USER,
        on_delete=models.CASCADE,
        verbose_name=gettext_lazy("User related to these permissions"),
    )
    can_add_members = models.BooleanField(default=False)
    can_remove_members = models.BooleanField(default=False)
    can_create_petitions = models.BooleanField(default=True)
    can_modify_petitions = models.BooleanField(default=True)
    can_delete_petitions = models.BooleanField(default=False)
    can_create_templates = models.BooleanField(default=True)
    can_modify_templates = models.BooleanField(default=True)
    can_delete_templates = models.BooleanField(default=False)
    can_view_signatures = models.BooleanField(default=False)
    can_modify_signatures = models.BooleanField(default=False)
    can_delete_signatures = models.BooleanField(default=False)
    can_modify_permissions = models.BooleanField(default=False)

    def set_all(self, value: bool) -> None:
        self.can_add_members = value
        self.can_remove_members = value
        self.can_create_petitions = value
        self.can_modify_petitions = value
        self.can_delete_petitions = value
        self.can_create_templates = value
        self.can_modify_templates = value
        self.can_delete_templates = value
        self.can_view_signatures = value
        self.can_modify_signatures = value
        self.can_delete_signatures = value
        self.can_modify_permissions = value
        self.save()

    def __str__(self) -> str:
        return f"{self.organization.name} : {self.user.name}"

    def __repr__(self) -> str:
        return f"< {self.__str__()} >"


# ------------------------------ Pre save actions -----------------------------
@receiver(pre_save, sender=SlugModel)
def check_slug_is_not_empty(sender: Any, instance: SlugModel, **kwargs: Any) -> None:
    instance.clean()
    instance.validate_unique()


# ------------------------------ Post save actions -----------------------------
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(
    sender: Any, instance: Any, created: bool, **kwargs: Any
) -> None:
    if created:
        PytitionUser.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender: Any, instance: Any, **kwargs: Any) -> None:
    instance.pytitionuser.save()


@receiver(pre_save, sender=Petition)
def pre_save_petition(sender: Any, instance: Petition, **kwargs: Any) -> None:
    if not instance.creation_date:
        instance.creation_date = timezone.now()


@receiver(post_save, sender=Petition)
def save_petition(sender: Any, instance: Petition, **kwargs: Any) -> None:
    if instance.slugmodel_set.count() == 0:
        instance.slugify()
    if kwargs.get("created"):
        instance.creation_date = timezone.now()
        instance.save()


@receiver(post_delete, sender=PytitionUser)
def post_delete_user(
    sender: Any, instance: PytitionUser, *args: Any, **kwargs: Any
) -> None:
    if instance.user:  # just in case user is not specified
        instance.user.delete()
