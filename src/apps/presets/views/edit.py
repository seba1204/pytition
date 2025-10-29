from __future__ import annotations

from collections.abc import Callable
from typing import Any

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
)
from django.shortcuts import render
from django.utils.translation import gettext as _

from apps.accounts.services import get_session_user
from apps.consents.forms import EmailForm, NewsletterForm
from apps.petition.models import PetitionTemplate, PytitionUser
from apps.petitions.forms import ContentFormTemplate, SocialNetworkForm, StyleForm
from apps.presets.services import (
    EditAccess,
    InternalPermissionError,
    ensure_user_can_edit_preset,
    get_presets_or_404,
    model_initial_from_form_fields,
    save_from_content_form,
    save_from_email_form,
    save_from_newsletter_form,
    save_from_social_form,
    save_from_style_form,
)


@login_required
def edit(request: HttpRequest, preset_id: int) -> HttpResponse:
    """
    Render and process the petition template edition page.

    Parameters
    ----------
    request : HttpRequest
        Authenticated Django request.
    preset_id : int
        Primary key of the template to edit.

    Returns
    -------
    HttpResponse
        Rendered HTML response for the edit page.

    Notes
    -----
    - Uses a single loop over form descriptors to avoid repetitive branches.
    - Delegates business logic to services for testability and reuse.
    """
    template: PetitionTemplate = get_presets_or_404(preset_id)
    user: PytitionUser = get_session_user(request)

    try:
        access: EditAccess = ensure_user_can_edit_preset(user, template)
    except InternalPermissionError:
        return HttpResponse(
            _(
                "Internal error, cannot find your permissions attached to this "
                "organization ('{orgname}')"
            ).format(orgname=(template.org.name if template.org else "")),
            status=500,
        )
    except Exception:
        return HttpResponseForbidden(_("You are not allowed to edit this template"))

    # Form configuration (name, FormClass, saver, exclude_initial_fields, uses_files)
    FormCfg = tuple[
        str,
        Any,  # the Django Form class
        Callable[..., None],  # the save_* service
        set[str] | None,
        bool,
    ]
    forms_cfg: list[FormCfg] = [
        ("content", ContentFormTemplate, save_from_content_form, None, False),
        ("email", EmailForm, save_from_email_form, None, False),
        (
            "social_network",
            SocialNetworkForm,
            save_from_social_form,
            {"twitter_image", "remove_twitter_image"},
            True,
        ),
        ("newsletter", NewsletterForm, save_from_newsletter_form, None, False),
        ("style", StyleForm, save_from_style_form, None, False),
    ]

    # Track submitted flags and concrete form instances for the template context
    submitted_flags: dict[str, bool] = {}
    bound_forms: dict[str, Any] = {}

    is_post: bool = request.method == "POST"
    storage = FileSystemStorage()  # Reused for social image when needed

    for name, form_cls, saver, exclude, uses_files in forms_cfg:
        submitted_key = f"{name}_form_submitted"
        was_submitted = is_post and (submitted_key in request.POST)
        submitted_flags[submitted_key] = was_submitted

        if was_submitted:
            form = (
                form_cls(request.POST, request.FILES)
                if uses_files
                else form_cls(request.POST)
            )
            if form.is_valid():
                # Social form requires special handling to pass the uploaded
                # file separately
                if form_cls is SocialNetworkForm:
                    cleaned: dict[str, Any] = dict(form.cleaned_data)
                    uploaded = cleaned.pop("twitter_image", None)
                    saver(
                        template=template,
                        cleaned=cleaned,
                        uploaded_twitter_image=uploaded,
                        storage=storage,
                        username=user.username,
                    )
                else:
                    saver(template, form.cleaned_data)
        else:
            initial = model_initial_from_form_fields(
                template, form_cls.base_fields, exclude=exclude
            )
            form = form_cls(initial)

        bound_forms[f"{name}_form"] = form

    context: dict[str, Any] = {
        "user": user,
        "base_template": access.base_template,
        "user_permissions": access.permissions,
        "org": access.org,
        "petition": template,
        "is_template": True,
        **bound_forms,
        **submitted_flags,
    }

    return render(request, "petition/edit_template.html", context)
