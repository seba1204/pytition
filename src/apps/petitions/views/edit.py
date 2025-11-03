from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from apps.accounts.models import Permission
from apps.accounts.routes import AccountsRoute
from apps.accounts.services import get_session_user
from apps.consents.forms import NewsletterForm
from apps.notifications.forms import EmailForm
from apps.petitions.forms import ContentFormPetition, SocialNetworkForm, StyleForm
from apps.petitions.helpers import petition_from_id


# FIXME: This view is too big, it should be split into smaller functions
# /<int:petition_id>/edit
# Edit a petition
@login_required
def edit(request: HttpRequest, petition_id: int) -> HttpResponse:  # noqa
    """
    Edit a petition view.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    petition_id : int
        The ID of the petition to edit.
    Returns
    -------
    HttpResponse
        The HTTP response object with the rendered edit petition page.
    """

    petition = petition_from_id(petition_id)
    pytitionuser = get_session_user(request)

    if not petition.is_allowed_to_edit(pytitionuser):
        messages.error(request, _("You are not allowed to edit this petition."))
        return redirect(AccountsRoute.DASHBOARD)

    submitted_ctx = {
        "content_form_submitted": False,
        "email_form_submitted": False,
        "social_network_form_submitted": False,
        "newsletter_form_submitted": False,
        "style_form_submitted": False,
    }

    if request.method == "POST":
        if "content_form_submitted" in request.POST:
            submitted_ctx["content_form_submitted"] = True
            content_form = ContentFormPetition(request.POST)
            if content_form.is_valid():
                petition.publication_date = content_form.cleaned_data[
                    "publication_date"
                ]
                petition.show_publication_date = content_form.cleaned_data[
                    "show_publication_date"
                ]
                petition.title = content_form.cleaned_data["title"]
                petition.target = content_form.cleaned_data["target"]
                petition.paper_signatures = content_form.cleaned_data[
                    "paper_signatures"
                ]
                petition.text = content_form.cleaned_data["text"]
                petition.side_text = content_form.cleaned_data["side_text"]
                petition.footer_text = content_form.cleaned_data["footer_text"]
                petition.footer_links = content_form.cleaned_data["footer_links"]
                petition.sign_form_footer = content_form.cleaned_data[
                    "sign_form_footer"
                ]
                petition.save()
        else:
            content_form = ContentFormPetition(
                {f: getattr(petition, f) for f in ContentFormPetition.base_fields}
            )

        if "email_form_submitted" in request.POST:
            submitted_ctx["email_form_submitted"] = True
            email_form = EmailForm(request.POST)
            if email_form.is_valid():
                petition.confirmation_email_reply = email_form.cleaned_data[
                    "confirmation_email_reply"
                ]
                petition.save()
        else:
            email_form = EmailForm(
                {f: getattr(petition, f) for f in EmailForm.base_fields}
            )

        if "social_network_form_submitted" in request.POST:
            submitted_ctx["social_network_form_submitted"] = True
            social_network_form = SocialNetworkForm(request.POST, request.FILES)
            if social_network_form.is_valid():
                storage = FileSystemStorage()
                file = social_network_form.cleaned_data["twitter_image"]
                if file:
                    path = Path(pytitionuser.username) / file.name
                    name = storage.save(str(path), file)
                    petition.twitter_image = storage.url(name)
                if social_network_form.cleaned_data["remove_twitter_image"]:
                    petition.twitter_image = ""
                petition.twitter_description = social_network_form.cleaned_data[
                    "twitter_description"
                ]
                petition.org_twitter_handle = social_network_form.cleaned_data[
                    "org_twitter_handle"
                ]
                petition.has_email_share_button = social_network_form.cleaned_data[
                    "has_email_share_button"
                ]
                petition.has_facebook_share_button = social_network_form.cleaned_data[
                    "has_facebook_share_button"
                ]
                petition.has_tumblr_share_button = social_network_form.cleaned_data[
                    "has_tumblr_share_button"
                ]
                petition.has_linkedin_share_button = social_network_form.cleaned_data[
                    "has_linkedin_share_button"
                ]
                petition.has_twitter_share_button = social_network_form.cleaned_data[
                    "has_twitter_share_button"
                ]
                petition.has_mastodon_share_button = social_network_form.cleaned_data[
                    "has_mastodon_share_button"
                ]
                petition.has_whatsapp_share_button = social_network_form.cleaned_data[
                    "has_whatsapp_share_button"
                ]
                petition.save()
        else:
            data = {
                "twitter_description": petition.twitter_description,
                "org_twitter_handle": petition.org_twitter_handle,
                "has_email_share_button": petition.has_email_share_button,
                "has_facebook_share_button": petition.has_facebook_share_button,
                "has_tumblr_share_button": petition.has_tumblr_share_button,
                "has_linkedin_share_button": petition.has_linkedin_share_button,
                "has_twitter_share_button": petition.has_twitter_share_button,
                "has_mastodon_share_button": petition.has_mastodon_share_button,
                "has_whatsapp_share_button": petition.has_whatsapp_share_button,
            }
            social_network_form = SocialNetworkForm(data)

        if "newsletter_form_submitted" in request.POST:
            submitted_ctx["newsletter_form_submitted"] = True
            newsletter_form = NewsletterForm(request.POST)
            if newsletter_form.is_valid():
                petition.has_newsletter = newsletter_form.cleaned_data["has_newsletter"]
                petition.newsletter_text = newsletter_form.cleaned_data[
                    "newsletter_text"
                ]
                petition.newsletter_subscribe_http_data = newsletter_form.cleaned_data[
                    "newsletter_subscribe_http_data"
                ]
                petition.newsletter_subscribe_http_mailfield = (
                    newsletter_form.cleaned_data["newsletter_subscribe_http_mailfield"]
                )
                petition.newsletter_subscribe_http_url = newsletter_form.cleaned_data[
                    "newsletter_subscribe_http_url"
                ]
                petition.newsletter_subscribe_mail_subject = (
                    newsletter_form.cleaned_data["newsletter_subscribe_mail_subject"]
                )
                petition.newsletter_subscribe_mail_from = newsletter_form.cleaned_data[
                    "newsletter_subscribe_mail_from"
                ]
                petition.newsletter_subscribe_mail_to = newsletter_form.cleaned_data[
                    "newsletter_subscribe_mail_to"
                ]
                petition.newsletter_subscribe_method = newsletter_form.cleaned_data[
                    "newsletter_subscribe_method"
                ]
                petition.newsletter_subscribe_mail_smtp_host = (
                    newsletter_form.cleaned_data["newsletter_subscribe_mail_smtp_host"]
                )
                petition.newsletter_subscribe_mail_smtp_port = (
                    newsletter_form.cleaned_data["newsletter_subscribe_mail_smtp_port"]
                )
                petition.newsletter_subscribe_mail_smtp_user = (
                    newsletter_form.cleaned_data["newsletter_subscribe_mail_smtp_user"]
                )
                petition.newsletter_subscribe_mail_smtp_password = (
                    newsletter_form.cleaned_data[
                        "newsletter_subscribe_mail_smtp_password"
                    ]
                )
                petition.newsletter_subscribe_mail_smtp_tls = (
                    newsletter_form.cleaned_data["newsletter_subscribe_mail_smtp_tls"]
                )
                petition.newsletter_subscribe_mail_smtp_starttls = (
                    newsletter_form.cleaned_data[
                        "newsletter_subscribe_mail_smtp_starttls"
                    ]
                )
                petition.save()
        else:
            newsletter_form = NewsletterForm(
                {f: getattr(petition, f) for f in NewsletterForm.base_fields}
            )

        if "style_form_submitted" in request.POST:
            submitted_ctx["style_form_submitted"] = True
            style_form = StyleForm(request.POST)
            if style_form.is_valid():
                petition.bgcolor = style_form.cleaned_data["bgcolor"]
                petition.linear_gradient_direction = style_form.cleaned_data[
                    "linear_gradient_direction"
                ]
                petition.gradient_from = style_form.cleaned_data["gradient_from"]
                petition.gradient_to = style_form.cleaned_data["gradient_to"]
                petition.save()
        else:
            style_form = StyleForm(
                {f: getattr(petition, f) for f in StyleForm.base_fields}
            )
    else:
        data = {
            "twitter_description": petition.twitter_description,
            "org_twitter_handle": petition.org_twitter_handle,
            "has_email_share_button": petition.has_email_share_button,
            "has_facebook_share_button": petition.has_facebook_share_button,
            "has_tumblr_share_button": petition.has_tumblr_share_button,
            "has_linkedin_share_button": petition.has_linkedin_share_button,
            "has_twitter_share_button": petition.has_twitter_share_button,
            "has_mastodon_share_button": petition.has_mastodon_share_button,
            "has_whatsapp_share_button": petition.has_whatsapp_share_button,
        }
        social_network_form = SocialNetworkForm(data)
        content_form = ContentFormPetition(
            {f: getattr(petition, f) for f in ContentFormPetition.base_fields}
        )
        style_form = StyleForm({f: getattr(petition, f) for f in StyleForm.base_fields})
        email_form = EmailForm({f: getattr(petition, f) for f in EmailForm.base_fields})
        newsletter_form = NewsletterForm(
            {f: getattr(petition, f) for f in NewsletterForm.base_fields}
        )

    ctx = {
        "user": pytitionuser,
        "content_form": content_form,
        "style_form": style_form,
        "email_form": email_form,
        "social_network_form": social_network_form,
        "newsletter_form": newsletter_form,
        "petition": petition,
        "is_template": False,
    }
    scheme = request.scheme if request.scheme is not None else "https"
    url_prefix = scheme + "://" + request.get_host()

    if petition.owner_type == "org":
        permissions = Permission.objects.get(
            organization=petition.org, user=pytitionuser
        )
        slug = petition.org.slugname if petition.org else ""
        example_url = url_prefix + reverse(
            "slug_show_petition",
            kwargs={
                "orgslugname": slug,
                "petitionname": _("save-the-kittens-from-bad-wolf"),
            },
        )
        slug_prefix = (
            url_prefix
            + reverse(
                "slug_show_petition",
                kwargs={"orgslugname": slug, "petitionname": "toto"},
            )
        ).rsplit("/", 1)[0]
        ctx.update(
            {
                "org": petition.org,
                "user_permissions": permissions,
                "base_template": "org/base.html",
                "example_url": example_url,
                "slug_prefix": slug_prefix,
            }
        )
    else:
        example_url = url_prefix + reverse(
            "slug_show_petition",
            kwargs={
                "username": pytitionuser.user.username,
                "petitionname": _("save-the-kittens-from-bad-wolf"),
            },
        )
        slug_prefix = (
            url_prefix
            + reverse(
                "slug_show_petition",
                kwargs={"username": pytitionuser.user.username, "petitionname": "toto"},
            )
        ).rsplit("/", 1)[0]
        ctx.update(
            {
                "base_template": "accounts/base.html",
                "example_url": example_url,
                "slug_prefix": slug_prefix,
            }
        )
    ctx.update(submitted_ctx)

    return render(request, "petitions/edit.html", ctx)
