"""Services related to petition presets (templates)."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.http import Http404
from django.utils.translation import gettext as _

from apps.accounts.models import Permission, PytitionUser
from apps.organizations.models import Organization
from apps.presets.models import PetitionTemplate


class FatalPermissionError(RuntimeError):
    """Represents an internal, non-user-fixable permission issue."""


class InternalPermissionError(RuntimeError):
    """Signals an internal configuration problem (e.g., missing Permission)."""


def ensure_user_can_delete_preset(
    user: PytitionUser, template: PetitionTemplate
) -> None:
    """
    Validate that `user` is allowed to delete `template`.

    Parameters
    ----------
    user : PytitionUser
        Currently authenticated Pytition user.
    template : PetitionTemplate
        Template targeted for deletion.

    Raises
    ------
    PermissionDenied
        If the user is not allowed to delete the template (403).
    FatalPermissionError
        If a required permission object is missing, implying a server-side issue (500).
    """
    # Determine the owner type in a flat, non-nested flow.
    if template.owner_type == "org":
        org: Organization | None = template.org
        # Owner must exist and user must be a member
        if org is None or user not in org.members.all():
            raise PermissionDenied("User is not a member of the organization.")

        try:
            perms: Permission = Permission.objects.get(organization=org, user=user)
        except Permission.DoesNotExist as exc:  # pragma: no cover - defensive
            # This mirrors the original behavior: treat as fatal (500)
            raise FatalPermissionError(
                "Missing Permission record for user/org."
            ) from exc

        if not perms.can_delete_templates:
            raise PermissionDenied("User lacks can_delete_templates.")
        return

    # Personal template case: only the owner can delete
    if template.user != user:
        raise PermissionDenied("User cannot delete another user's template.")


@dataclass(frozen=True)
class EditAccess:
    """
    Represents view-layer needs for editing a template.

    Attributes
    ----------
    base_template : str
        The base template path to extend from (org vs user).
    permissions : Optional[Permission]
        Organization-scoped permissions if owner is an organization, else None.
    org : Optional[Organization]
        Organization instance when owner_type is 'org', else None.
    """

    base_template: str
    permissions: Permission | None
    org: Organization | None


def get_presets_or_404(preset_id: int) -> PetitionTemplate:
    """
    Fetch a PetitionTemplate or raise 404.

    Parameters
    ----------
    preset_id : int
        Template primary key.

    Returns
    -------
    PetitionTemplate
        The template instance.

    Raises
    ------
    Http404
        If the template does not exist.
    """
    try:
        return PetitionTemplate.objects.get(pk=preset_id)
    except PetitionTemplate.DoesNotExist as err:
        raise Http404(_("This template does not exist.")) from err


def ensure_user_can_edit_preset(
    user: PytitionUser, preset: PetitionTemplate
) -> EditAccess:
    """
    Validate edit access and return rendering metadata.

    Parameters
    ----------
    user : PytitionUser
        Current authenticated user.
    preset : PetitionTemplate
        Target preset.

    Returns
    -------
    EditAccess
        Access metadata (base preset, permissions, org).

    Raises
    ------
    PermissionDenied
        If the user is not allowed to edit the preset.
    InternalPermissionError
        If an expected Permission record is missing (internal error).
    """
    if preset.owner_type == "org":
        org: Organization | None = preset.org
        if org is None or user not in org.members.all():
            raise PermissionDenied("User is not a member of the organization.")
        try:
            perms: Permission = Permission.objects.get(organization=org, user=user)
        except Permission.DoesNotExist as exc:
            raise InternalPermissionError(
                "Missing Permission record for user/org."
            ) from exc
        if not perms.can_modify_templates:
            raise PermissionDenied("User lacks can_modify_templates.")

        return EditAccess(
            base_template="org/base.html",
            permissions=perms,
            org=org,
        )

    # Personal ownership: only the owner can edit
    if preset.user != user:
        raise PermissionDenied("User cannot edit another user's preset.")

    return EditAccess(
        base_template="accounts/base.html",
        permissions=None,
        org=None,
    )


def model_initial_from_form_fields(
    instance: Any,
    form_base_fields: Mapping[str, Any],
    *,
    exclude: Iterable[str] | None = None,
) -> dict[str, Any]:
    """
    Build initial dict for a form using model attributes.

    Parameters
    ----------
    instance : Any
        Model instance to read from.
    form_base_fields : Mapping[str, Any]
        Form base fields (e.g., `MyForm.base_fields`).
    exclude : Iterable[str] or None
        Field names to exclude from the initial payload.

    Returns
    -------
    dict
        Mapping of field name to value taken from the model.
    """
    excl: set[str] = set(exclude or ())
    out: dict[str, Any] = {}
    for name in form_base_fields:
        if name in excl:
            continue
        out[name] = getattr(instance, name, None)
    return out


def save_from_content_form(
    template: PetitionTemplate, cleaned: Mapping[str, Any]
) -> None:
    """
    Persist content-related fields coming from ContentFormTemplate.

    Parameters
    ----------
    template : PetitionTemplate
        Template to update.
    cleaned : Mapping[str, Any]
        Validated form data.
    """
    template.target = cleaned["target"]
    template.name = cleaned["name"]
    template.text = cleaned["text"]
    template.side_text = cleaned["side_text"]
    template.footer_text = cleaned["footer_text"]
    template.footer_links = cleaned["footer_links"]
    template.sign_form_footer = cleaned["sign_form_footer"]
    template.save(
        update_fields=[
            "target",
            "name",
            "text",
            "side_text",
            "footer_text",
            "footer_links",
            "sign_form_footer",
        ]
    )


def save_from_email_form(
    template: PetitionTemplate, cleaned: Mapping[str, Any]
) -> None:
    """Persist email-related fields coming from EmailForm."""
    template.confirmation_email_reply = cleaned["confirmation_email_reply"]
    template.save(update_fields=["confirmation_email_reply"])


def save_from_social_form(
    *,
    template: PetitionTemplate,
    cleaned: Mapping[str, Any],
    uploaded_twitter_image: Any | None,
    storage: FileSystemStorage,
    username: str,
) -> None:
    """
    Persist social-network-related fields, handling optional image.

    Parameters
    ----------
    template : PetitionTemplate
        Template to update.
    cleaned : Mapping[str, Any]
        Validated form data (excluding the uploaded file object).
    uploaded_twitter_image : Any or None
        Uploaded file object for twitter image, if any.
    storage : FileSystemStorage
        Storage backend used to save files.
    username : str
        Username used to namespace media paths.
    """
    if uploaded_twitter_image:
        path = Path(username) / cast(str, uploaded_twitter_image.name)
        name = storage.save(str(path), uploaded_twitter_image)
        template.twitter_image = storage.url(name)

    if cleaned.get("remove_twitter_image"):
        template.twitter_image = ""

    # Boolean toggles and text fields
    keys_to_copy = [
        "twitter_description",
        "org_twitter_handle",
        "has_email_share_button",
        "has_facebook_share_button",
        "has_tumblr_share_button",
        "has_linkedin_share_button",
        "has_twitter_share_button",
        "has_mastodon_share_button",
        "has_whatsapp_share_button",
    ]
    for k in keys_to_copy:
        setattr(template, k, cleaned[k])

    template.save(update_fields=["twitter_image"] + keys_to_copy)


def save_from_newsletter_form(
    template: PetitionTemplate, cleaned: Mapping[str, Any]
) -> None:
    """Persist newsletter-related fields coming from NewsletterForm."""
    keys = [
        "has_newsletter",
        "newsletter_text",
        "newsletter_subscribe_http_data",
        "newsletter_subscribe_http_mailfield",
        "newsletter_subscribe_http_url",
        "newsletter_subscribe_mail_subject",
        "newsletter_subscribe_mail_from",
        "newsletter_subscribe_mail_to",
        "newsletter_subscribe_method",
        "newsletter_subscribe_mail_smtp_host",
        "newsletter_subscribe_mail_smtp_port",
        "newsletter_subscribe_mail_smtp_user",
        "newsletter_subscribe_mail_smtp_password",
        "newsletter_subscribe_mail_smtp_tls",
        "newsletter_subscribe_mail_smtp_starttls",
    ]
    for k in keys:
        setattr(template, k, cleaned[k])
    template.save(update_fields=keys)


def save_from_style_form(
    template: PetitionTemplate, cleaned: Mapping[str, Any]
) -> None:
    """Persist style-related fields coming from StyleForm."""
    template.bgcolor = cleaned["bgcolor"]
    template.linear_gradient_direction = cleaned["linear_gradient_direction"]
    template.gradient_from = cleaned["gradient_from"]
    template.gradient_to = cleaned["gradient_to"]
    template.save(
        update_fields=[
            "bgcolor",
            "linear_gradient_direction",
            "gradient_from",
            "gradient_to",
        ]
    )
