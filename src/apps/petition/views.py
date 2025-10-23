import random
from pathlib import Path
from time import time
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
)
from django.http import HttpResponse as DjangoHttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.generic.edit import CreateView

from apps.consents.forms import EmailForm, NewsletterForm
from apps.organizations.routes import OrgRoute
from apps.petition.forms import (
    DeleteAccountForm,
    PytitionUserCreationForm,
    UpdateInfoForm,
)
from apps.petition.helpers import (
    get_session_user,
    get_update_form,
    petition_from_id,
    remove_user_moderated,
)
from apps.petition.models import (
    Moderation,
    ModerationReason,
    Organization,
    Permission,
    Petition,
    PetitionTemplate,
    PytitionUser,
)
from apps.petitions.forms import ContentFormTemplate, SocialNetworkForm, StyleForm


def index(request: HttpRequest) -> DjangoHttpResponse:
    if not hasattr(settings, "INDEX_PAGE"):
        raise Http404(_("You must set an INDEX_PAGE config in your settings"))
    index_page = getattr(settings, "INDEX_PAGE", None)
    if index_page == "USER_PROFILE":
        user_name = getattr(settings, "INDEX_PAGE_USER", None)
        if not isinstance(user_name, str) or not user_name:
            raise Http404(_("You must set an INDEX_PAGE_USER config in your settings"))
    elif index_page == "ORGA_PROFILE":
        org_name = getattr(settings, "INDEX_PAGE_ORGA", None)
        if not isinstance(org_name, str) or not org_name:
            raise Http404(_("You must set an INDEX_PAGE_ORGA config in your settings"))

    if index_page == "ORGA_PROFILE":
        org = Organization.objects.get(name=org_name)
        return redirect(OrgRoute.PROFILE, org.slugname)
    elif index_page == "USER_PROFILE":
        return redirect("user_profile", user_name)
    elif settings.INDEX_PAGE == "LOGIN_REGISTER":
        if request.user.is_authenticated:
            return redirect("user_dashboard")
        else:
            return redirect("login")
    else:
        authenticated = request.user.is_authenticated
        user = get_session_user(request) if authenticated else request.user
        sort = request.GET.get("sort", "desc")
        creation_date = "-creation_date" if sort == "desc" else "creation_date"
        all_petitions_qs = Petition.objects.filter(
            published=True, moderated=False
        ).order_by(creation_date)
        all_petitions = remove_user_moderated(list(all_petitions_qs))
        paginator = Paginator(all_petitions, settings.PAGINATOR_COUNT)
        page = request.GET.get("page")
        petitions = paginator.get_page(page)

        return render(
            request,
            "petition/index.html",
            {"user": user, "petitions": petitions, "sort": sort},
        )


# /search?q=QUERY
# Show results of a search query
def search(request: HttpRequest) -> HttpResponse:
    q = request.GET.get("q", "")
    if q != "":
        petitions_qs = Petition.objects.filter(
            Q(title__icontains=q) | Q(text__icontains=q)
        ).filter(published=True, moderated=False)[:15]
        petitions = remove_user_moderated(list(petitions_qs))
        orgs = list(Organization.objects.filter(name__icontains=q))
    else:
        petitions_qs = Petition.objects.filter(
            published=True, moderated=False
        ).order_by("-id")
        petitions = remove_user_moderated(list(petitions_qs))
        paginator = Paginator(petitions, settings.PAGINATOR_COUNT)
        page = request.GET.get("page")
        petitions = paginator.get_page(page)
        orgs: list[Any] = []
    return render(
        request, "petition/search.html", {"petitions": petitions, "orgs": orgs, "q": q}
    )


# /user/dashboard
# Dashboard of the logged in user
@login_required
def user_dashboard(request: HttpRequest) -> HttpResponse:
    user = get_session_user(request)
    petitions = user.petition_set.all()

    return render(
        request,
        "petition/user_dashboard.html",
        {
            "user": user,
            "petitions": petitions,
            "can_create_petition": True,
            "displaying_dashboard": True,
        },
    )


# /user/<user_name>
# Show the user profile
def user_profile(request: HttpRequest, user_name: str) -> HttpResponse:
    try:
        user = PytitionUser.objects.get(user__username=user_name)
    except PytitionUser.DoesNotExist as err:
        raise Http404(_("not found")) from err
    sort = request.GET.get("sort", "desc")
    creation_date = "-creation_date" if sort == "desc" else "creation_date"
    petitions_qs = user.petition_set.filter(published=True, moderated=False).order_by(
        creation_date
    )
    petitions_list = remove_user_moderated(list(petitions_qs))
    paginator = Paginator(petitions_list, settings.PAGINATOR_COUNT)
    page = request.GET.get("page")
    petitions = paginator.get_page(page)

    return render(
        request,
        "petition/user_profile.html",
        {"user": user, "petitions": petitions, "sort": sort},
    )


# /get_user_list
# get the list of users
@login_required
def get_user_list(request: HttpRequest) -> JsonResponse:
    q = request.GET.get("q", "")
    if q != "":
        users = PytitionUser.objects.filter(
            Q(user__username__contains=q)
            | Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
        ).all()
    else:
        users = PytitionUser.objects.none()

    userdict = {
        "values": [user.user.username for user in users],
    }
    return JsonResponse(userdict)


# /templates/<int:template_id>/edit
# Edit a petition template
@login_required
def edit_template(request: HttpRequest, template_id: int) -> HttpResponse:
    id = template_id

    try:
        template = PetitionTemplate.objects.get(pk=id)
    except PetitionTemplate.DoesNotExist as err:
        raise Http404(_("This template does not exist")) from err

    pytitionuser = get_session_user(request)
    context = {"user": pytitionuser}

    owner: Organization | PytitionUser | None = (
        template.org if template.owner_type == "org" else template.user
    )

    if template.owner_type == "org":
        try:
            permissions = Permission.objects.get(organization=owner, user=pytitionuser)
        except Exception:
            return HttpResponse(
                _(
                    "Internal error, cannot find your permissions attached to this "
                    "organization ('{orgname}')".format(orgname=owner.name)
                ),
                status=500,
            )
        context["user_permissions"] = permissions
        if (
            owner not in pytitionuser.organization_set.all()
            or not permissions.can_modify_templates
        ):
            return HttpResponseForbidden(
                _("You are not allowed to edit this organization's templates")
            )
        context["org"] = owner
        base_template = "org/base.html"
    else:
        if owner != pytitionuser:
            return HttpResponseForbidden(
                _("You are not allowed to edit this user's templates")
            )
        base_template = "petition/user_base.html"

    submitted_ctx = {
        "content_form_submitted": False,
        "email_form_submitted": False,
        "social_network_form_submitted": False,
        "newsletter_form_submitted": False,
        "style_form_submitted": False,
    }

    if request.method == "POST":
        if "content_form_submitted" in request.POST:
            content_form = ContentFormTemplate(request.POST)
            submitted_ctx["content_form_submitted"] = True
            if content_form.is_valid():
                template.target = content_form.cleaned_data["target"]
                template.name = content_form.cleaned_data["name"]
                template.text = content_form.cleaned_data["text"]
                template.side_text = content_form.cleaned_data["side_text"]
                template.footer_text = content_form.cleaned_data["footer_text"]
                template.footer_links = content_form.cleaned_data["footer_links"]
                template.sign_form_footer = content_form.cleaned_data[
                    "sign_form_footer"
                ]
                template.save()
        else:
            content_form = ContentFormTemplate(
                {f: getattr(template, f) for f in ContentFormTemplate.base_fields}
            )

        if "email_form_submitted" in request.POST:
            email_form = EmailForm(request.POST)
            submitted_ctx["email_form_submitted"] = True
            if email_form.is_valid():
                template.confirmation_email_reply = email_form.cleaned_data[
                    "confirmation_email_reply"
                ]
                template.save()
        else:
            email_form = EmailForm(
                {f: getattr(template, f) for f in EmailForm.base_fields}
            )

        if "social_network_form_submitted" in request.POST:
            social_network_form = SocialNetworkForm(request.POST, request.FILES)
            submitted_ctx["social_network_form_submitted"] = True
            if social_network_form.is_valid():
                storage = FileSystemStorage()
                file = social_network_form.cleaned_data["twitter_image"]
                if file:
                    path = Path(pytitionuser.username) / file.name
                    name = storage.save(str(path), file)
                    template.twitter_image = storage.url(name)
                if social_network_form.cleaned_data["remove_twitter_image"]:
                    template.twitter_image = ""
                template.twitter_description = social_network_form.cleaned_data[
                    "twitter_description"
                ]
                template.org_twitter_handle = social_network_form.cleaned_data[
                    "org_twitter_handle"
                ]
                template.has_email_share_button = social_network_form.cleaned_data[
                    "has_email_share_button"
                ]
                template.has_facebook_share_button = social_network_form.cleaned_data[
                    "has_facebook_share_button"
                ]
                template.has_tumblr_share_button = social_network_form.cleaned_data[
                    "has_tumblr_share_button"
                ]
                template.has_linkedin_share_button = social_network_form.cleaned_data[
                    "has_linkedin_share_button"
                ]
                template.has_twitter_share_button = social_network_form.cleaned_data[
                    "has_twitter_share_button"
                ]
                template.has_mastodon_share_button = social_network_form.cleaned_data[
                    "has_mastodon_share_button"
                ]
                template.has_whatsapp_share_button = social_network_form.cleaned_data[
                    "has_whatsapp_share_button"
                ]
                template.save()
        else:
            remove_fields = ["twitter_image", "remove_twitter_image"]
            fields = {
                k: v
                for k, v in SocialNetworkForm.base_fields.items()
                if k not in remove_fields
            }
            social_network_form = SocialNetworkForm(
                {f: getattr(template, f) for f in fields}
            )

        if "newsletter_form_submitted" in request.POST:
            newsletter_form = NewsletterForm(request.POST)
            submitted_ctx["newsletter_form_submitted"] = True
            if newsletter_form.is_valid():
                template.has_newsletter = newsletter_form.cleaned_data["has_newsletter"]
                template.newsletter_text = newsletter_form.cleaned_data[
                    "newsletter_text"
                ]
                template.newsletter_subscribe_http_data = newsletter_form.cleaned_data[
                    "newsletter_subscribe_http_data"
                ]
                template.newsletter_subscribe_http_mailfield = (
                    newsletter_form.cleaned_data["newsletter_subscribe_http_mailfield"]
                )
                template.newsletter_subscribe_http_url = newsletter_form.cleaned_data[
                    "newsletter_subscribe_http_url"
                ]
                template.newsletter_subscribe_mail_subject = (
                    newsletter_form.cleaned_data["newsletter_subscribe_mail_subject"]
                )
                template.newsletter_subscribe_mail_from = newsletter_form.cleaned_data[
                    "newsletter_subscribe_mail_from"
                ]
                template.newsletter_subscribe_mail_to = newsletter_form.cleaned_data[
                    "newsletter_subscribe_mail_to"
                ]
                template.newsletter_subscribe_method = newsletter_form.cleaned_data[
                    "newsletter_subscribe_method"
                ]
                template.newsletter_subscribe_mail_smtp_host = (
                    newsletter_form.cleaned_data["newsletter_subscribe_mail_smtp_host"]
                )
                template.newsletter_subscribe_mail_smtp_port = (
                    newsletter_form.cleaned_data["newsletter_subscribe_mail_smtp_port"]
                )
                template.newsletter_subscribe_mail_smtp_user = (
                    newsletter_form.cleaned_data["newsletter_subscribe_mail_smtp_user"]
                )
                template.newsletter_subscribe_mail_smtp_password = (
                    newsletter_form.cleaned_data[
                        "newsletter_subscribe_mail_smtp_password"
                    ]
                )
                template.newsletter_subscribe_mail_smtp_tls = (
                    newsletter_form.cleaned_data["newsletter_subscribe_mail_smtp_tls"]
                )
                template.newsletter_subscribe_mail_smtp_starttls = (
                    newsletter_form.cleaned_data[
                        "newsletter_subscribe_mail_smtp_starttls"
                    ]
                )
                template.save()
        else:
            newsletter_form = NewsletterForm(
                {f: getattr(template, f) for f in NewsletterForm.base_fields}
            )

        if "style_form_submitted" in request.POST:
            submitted_ctx["style_form_submitted"] = True
            style_form = StyleForm(request.POST)
            if style_form.is_valid():
                template.bgcolor = style_form.cleaned_data["bgcolor"]
                template.linear_gradient_direction = style_form.cleaned_data[
                    "linear_gradient_direction"
                ]
                template.gradient_from = style_form.cleaned_data["gradient_from"]
                template.gradient_to = style_form.cleaned_data["gradient_to"]
                template.save()
        else:
            style_form = StyleForm(
                {f: getattr(template, f) for f in StyleForm.base_fields}
            )
    else:
        remove_fields = ["twitter_image", "remove_twitter_image"]
        fields = {
            k: v
            for k, v in SocialNetworkForm.base_fields.items()
            if k not in remove_fields
        }
        social_network_form = SocialNetworkForm(
            {f: getattr(template, f) for f in fields}
        )
        content_form = ContentFormTemplate(
            {f: getattr(template, f) for f in ContentFormTemplate.base_fields}
        )
        email_form = EmailForm({f: getattr(template, f) for f in EmailForm.base_fields})
        newsletter_form = NewsletterForm(
            {f: getattr(template, f) for f in NewsletterForm.base_fields}
        )
        style_form = StyleForm({f: getattr(template, f) for f in StyleForm.base_fields})

    ctx = {
        "content_form": content_form,
        "email_form": email_form,
        "social_network_form": social_network_form,
        "newsletter_form": newsletter_form,
        "style_form": style_form,
        "petition": template,
        "is_template": True,
    }

    context["base_template"] = base_template
    context.update(ctx)
    context.update(submitted_ctx)
    return render(request, "petition/edit_template.html", context)


# /templates/<int:template_id>/delete
# Delete a template
@login_required
def template_delete(request: HttpRequest, template_id: int) -> JsonResponse:
    pytitionuser = get_session_user(request)
    if template_id == "":
        return JsonResponse({}, status=500)

    try:
        template = PetitionTemplate.objects.get(pk=template_id)
    except Exception:
        return JsonResponse({}, status=404)

    if template.owner_type == "org":
        if pytitionuser not in template.org.members.all():
            return JsonResponse({}, status=403)  # User not in organization
        try:
            permissions = Permission.objects.get(
                organization=template.org, user=pytitionuser
            )
        except Permission.DoesNotExist:
            return JsonResponse({}, status=500)  # No permission? fatal error!
        if not permissions.can_delete_templates:
            return JsonResponse({}, status=403)  # User does not have the permission!
    elif pytitionuser != template.user:
        return JsonResponse(
            {}, status=403
        )  # User cannot delete a template if it's not his
    template.delete()
    return JsonResponse({})


# /templates/<int:template_id>/fav
# Set a template as favorite
@login_required
def template_fav_toggle(request: HttpRequest, template_id: int) -> JsonResponse:
    pytitionuser = get_session_user(request)
    if template_id == "":
        return JsonResponse({}, status=500)

    try:
        template = PetitionTemplate.objects.get(pk=template_id)
    except PetitionTemplate.DoesNotExist:
        return JsonResponse({}, status=404)

    owner = template.org if template.owner_type == "org" else template.user

    if template.owner_type == "org":
        if owner not in pytitionuser.organization_set.all():
            return JsonResponse({}, status=403)  # Forbidden
    elif owner != pytitionuser:
        return JsonResponse(
            {"msg": _("You are not allowed to change this user's default template")},
            status=403,
        )

    if owner.default_template == template:
        owner.default_template = None
    else:
        owner.default_template = template
    owner.save()

    return JsonResponse({})


# /account_settings
# Show settings for the user accounts
@login_required
def account_settings(request: HttpRequest) -> HttpResponse:
    pytitionuser = get_session_user(request)
    submitted_ctx = {
        "update_info_form_submitted": False,
        "delete_account_form_submitted": False,
        "password_change_form_submitted": False,
    }

    if request.method == "POST":
        if "update_info_form_submitted" in request.POST:
            update_info_form = UpdateInfoForm(pytitionuser.user, request.POST)
            submitted_ctx["update_info_form_submitted"] = True
            if update_info_form.is_valid():
                update_info_form.save()
        else:
            update_info_form = get_update_form(pytitionuser.user)

        if "delete_account_form_submitted" in request.POST:
            delete_account_form = DeleteAccountForm(request.POST)
            submitted_ctx["delete_account_form_submitted"] = True
            if delete_account_form.is_valid():
                pytitionuser.drop()
                return redirect("index")
        else:
            delete_account_form = DeleteAccountForm()

        if "password_change_form_submitted" in request.POST:
            password_change_form = PasswordChangeForm(pytitionuser.user, request.POST)
            submitted_ctx["password_change_form_submitted"] = True
            if password_change_form.is_valid():
                password_change_form.save()
                messages.success(request, _("You successfully changed your password!"))
        else:
            password_change_form = PasswordChangeForm(pytitionuser.user)

    else:
        update_info_form = get_update_form(pytitionuser.user)
        delete_account_form = DeleteAccountForm()
        password_change_form = PasswordChangeForm(pytitionuser.user)

    orgs = pytitionuser.organization_set.all()
    # Checking if the user is allowed to leave the organization

    MIN_ORG_MEMBERS = 2

    for org in orgs:
        if org.members.count() < MIN_ORG_MEMBERS:
            org.leave = False
        else:
            # More than one user, we need to check owners
            owners = org.owners.all()
            if owners.count() == 1 and pytitionuser in owners:
                org.leave = False
            else:
                org.leave = True

    ctx = {
        "user": pytitionuser,
        "update_info_form": update_info_form,
        "delete_account_form": delete_account_form,
        "password_change_form": password_change_form,
        "base_template": "petition/user_base.html",
        "orgs": orgs,
    }
    ctx.update(submitted_ctx)

    return render(request, "petition/account_settings.html", ctx)


@login_required
def image_upload(request: HttpRequest) -> HttpResponse:
    pytitionuser = get_session_user(request)

    if request.method != "POST":
        return HttpResponseForbidden()

    file = request.FILES.get("file", "")
    if file == "":
        return HttpResponseForbidden()

    storage = FileSystemStorage()
    path = Path(pytitionuser.username) / file.name
    name = storage.save(str(path), file)
    return JsonResponse({"location": storage.url(name)})


@login_required
def search_users_and_orgs(request: HttpRequest) -> JsonResponse:
    query = request.GET.get("q", "")
    if query != "":
        users = PytitionUser.objects.filter(
            Q(user__username__contains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
        ).all()
        orgs = Organization.objects.filter(name__icontains=query).all()
    else:
        users = []
        orgs = []

    result = {
        "orgs": [{"slugname": org.slugname, "name": org.name} for org in orgs],
        "users": [
            {
                "username": user.user.username,
                "firstname": user.user.first_name,
                "lastname": user.user.last_name,
            }
            for user in users
        ],
    }
    return JsonResponse(result)


class PytitionUserCreateView(CreateView):
    def save_numbers(self, request: HttpRequest) -> None:
        request.session["random_a"] = self.a
        request.session["random_b"] = self.b
        request.session["answer"] = self.answer

    def get_new_numbers(self) -> None:
        r = random.Random(time())
        self.a = r.choice(range(0, 100))
        self.b = r.choice(range(0, 100))
        self.answer = self.a + self.b
        self.form_class.base_fields["answer"].label = _(
            "How much is {a} + {b}?"
        ).format(a=self.a, b=self.b)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.get_new_numbers()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        self.save_numbers(self.request)
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs

    def form_valid(self, form: PytitionUserCreationForm) -> HttpResponse:
        form.send_success_email()
        return super().form_valid(form)


# /<int:petition_id>/report/<int:reason_id>
# Report a petition to moderation
def report_petition(
    request: HttpRequest, petition_id: int, reason_id: int | None = None
) -> HttpResponse:
    petition = petition_from_id(petition_id)
    if reason_id:
        try:
            reason = ModerationReason.objects.get(pk=reason_id)
        except Exception:
            return HttpResponse(status=500)

    if reason_id:
        Moderation.objects.create(petition=petition, reason=reason)
    else:
        Moderation.objects.create(petition=petition)
    return HttpResponse(status=200)
