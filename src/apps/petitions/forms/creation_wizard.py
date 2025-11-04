"""Petition creation wizard form."""

from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from formtools.wizard.views import SessionWizardView  # type: ignore

from apps.accounts.models import Permission
from apps.accounts.routes import AccountsRoute
from apps.accounts.services import get_session_user
from apps.organizations.models import Organization
from apps.organizations.routes import OrgRoute
from apps.petitions.models import Petition
from apps.petitions.routes import PetitionsRoute
from apps.presets.models import PetitionTemplate

from .creation_steps import (
    PetitionCreationStep1,
    PetitionCreationStep2,
    PetitionCreationStep3,
)

WizardForms = [
    ("step1", PetitionCreationStep1),
    ("step2", PetitionCreationStep2),
    ("step3", PetitionCreationStep3),
]

WizardTemplates = {
    "step1": "petitions/new_step1.html",
    "step2": "petitions/new_step2.html",
    "step3": "petitions/new_step3.html",
}

SESSION_KEY = "wizard_params:petition_creation"


# Class Based Controller
# PATH : subroutes of /wizard
@method_decorator(login_required, name="dispatch")
class PetitionCreationWizard(SessionWizardView):
    """Wizard for creating a petition."""

    def _load_params_from_session_or_get(self) -> None:
        """Load/merge parameters from the session and query string."""
        session_data = self.request.session
        data = dict(session_data.get(SESSION_KEY, {}))

        org = self.request.GET.get("org")
        tpl = self.request.GET.get("template_id")

        updated = False
        if org is not None:
            data["orgslugname"] = org
            updated = True
        if tpl and str(tpl).isdigit():
            data["template_id"] = int(tpl)
            updated = True

        # If nothing in GET and nothing in session, data remains empty -> “user” mode
        if updated or SESSION_KEY not in session_data:
            session_data[SESSION_KEY] = data
            session_data.modified = True

        # cache on the instance to avoid re-reading the session 50 times
        self._wizard_params = data

    def _clear_params_session(self) -> None:
        """Clear the wizard parameters from the session."""
        self.request.session.pop(SESSION_KEY, None)
        self.request.session.modified = True

    def _orgslugname(self) -> str | None:
        """Get the organization slugname if any."""
        value = (getattr(self, "_wizard_params", None) or {}).get("orgslugname")
        if value is not None:
            return str(value)
        value = self.kwargs.get("orgslugname")
        if value is not None:
            return str(value)
        return None

    def _template_id(self) -> int | None:
        """Get the template ID if any."""
        value = (getattr(self, "_wizard_params", None) or {}).get("template_id")
        if value is None:
            value = self.kwargs.get("template_id")
        if value is not None and isinstance(value, str) and value.isdigit():
            return int(value)
        if isinstance(value, int):
            return value
        return None

    def _is_org_petition(self) -> bool:
        """Check if the petition is to be created under an organization."""
        return self._orgslugname() is not None

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        """Load parameters and check if user can create petitions."""
        self._load_params_from_session_or_get()
        if settings.DISABLE_USER_PETITION and not self._is_org_petition():
            messages.error(
                request, _("Users are not allowed to create their own petitions.")
            )
            return redirect(AccountsRoute.DASHBOARD)
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self) -> list[str]:
        """Get the template name for the current step."""
        return [WizardTemplates[self.steps.current]]

    def get_form_initial(self, step: str) -> dict[str, Any]:
        """Get initial data for the given step."""
        template = None
        org_petition = self._is_org_petition()
        if org_petition:
            orgslugname = self._orgslugname()
            org = Organization.objects.get(slugname=orgslugname)
        else:
            pytitionuser = get_session_user(self.request)

        tpl_id = self._template_id()
        if tpl_id is not None:
            template = PetitionTemplate.objects.get(pk=tpl_id)
        elif org_petition:
            template = org.default_template
        else:
            template = pytitionuser.default_template

        # Check the template is actually ours
        if template is not None and org_petition:
            if template not in org.petitiontemplate_set.all():
                template = None
        elif (
            template is not None
            and template not in pytitionuser.petitiontemplate_set.all()
        ):
            template = None

        if step == "step2" and template is not None:
            return {"message": template.text}

        if step == "step3":
            if template is not None:
                return {"use_template": True, "template_id": template.id}
            else:
                return {"use_template": False, "template_id": 0}

        return dict(self.initial_dict.get(step, {}) or {})

    def get_form_kwargs(self, step: str | None = None) -> dict[str, Any]:
        """Get extra kwargs for the given step."""
        if step == "step1":
            if self._is_org_petition():
                return {"orgslugname": self._orgslugname()}
            else:
                pytitionuser = get_session_user(self.request)
                return {"user_name": pytitionuser.user.username}
        return {}

    # FIXME: this method is too long, split it into smaller methods
    def done(self, form_list: list[Any], **kwargs: Any) -> HttpResponse:  # noqa
        """Create the petition and redirect to the appropriate page."""
        try:
            org_petition = self._is_org_petition()
            title = self.get_cleaned_data_for_step("step1")["title"]
            message = self.get_cleaned_data_for_step("step2")["message"]
            publish = self.get_cleaned_data_for_step("step3")["publish"]
            template_id = self.get_cleaned_data_for_step("step3")["template_id"]
            use_template = self.get_cleaned_data_for_step("step3")["use_template"]
            pytitionuser = get_session_user(self.request)
            _redirect = self.request.POST.get("redirect", "")

            if org_petition:
                orgslugname = self._orgslugname()
                try:
                    org = Organization.objects.get(slugname=orgslugname)
                except Organization.DoesNotExist:
                    messages.error(self.request, _("Cannot find this organization."))
                    return redirect(AccountsRoute.DASHBOARD)

                try:
                    permissions = Permission.objects.get(
                        organization=org, user=pytitionuser
                    )
                except Permission.DoesNotExist:
                    return redirect(OrgRoute.DASHBOARD, orgslugname)

                if (
                    pytitionuser in org.members.all()
                    and permissions.can_create_petitions
                ):
                    petition = Petition.objects.create(
                        title=title, text=message, org=org
                    )
                    if use_template:
                        template = PetitionTemplate.objects.get(pk=template_id)
                        if template in org.petitiontemplate_set.all():
                            petition.prepopulate_from_template(
                                template, exclude_fields=["text"]
                            )
                            petition.save()
                        else:
                            messages.error(
                                self.request,
                                _(
                                    "This template does not belong to your "
                                    "organization."
                                ),
                            )
                            return redirect(OrgRoute.DASHBOARD, orgslugname)
                    if publish:
                        petition.publish()
                    if _redirect and _redirect == "1":
                        return redirect(PetitionsRoute.EDIT, petition.id)
                    return redirect(OrgRoute.DASHBOARD, orgslugname)
                else:
                    messages.error(
                        self.request,
                        _(
                            "You don't have the permission to create a new petition in "
                            "this Organization."
                        ),
                    )
                    return redirect(OrgRoute.DASHBOARD, orgslugname)
            else:
                petition = Petition.objects.create(
                    title=title, text=message, user=pytitionuser
                )
                if use_template:
                    template = PetitionTemplate.objects.get(pk=template_id)
                    if template in pytitionuser.petitiontemplate_set.all():
                        petition.prepopulate_from_template(
                            template, exclude_fields=["text"]
                        )
                        petition.save()
                    else:
                        messages.error(
                            self.request, _("This template does not belong to you.")
                        )
                        return redirect(AccountsRoute.DASHBOARD)
                if publish:
                    petition.publish()
                if _redirect and _redirect == "1":
                    return redirect(PetitionsRoute.EDIT, petition.id)
                return redirect(AccountsRoute.DASHBOARD)
        finally:
            self._clear_params_session()

    def get_context_data(self, form: Any, **kwargs: Any) -> dict[str, Any]:
        """Get context data for the template rendering."""
        org_petition = self._is_org_petition()
        context = super().get_context_data(form=form, **kwargs)
        if org_petition:
            base_template = "org/base.html"
            try:
                org = Organization.objects.get(slugname=self._orgslugname())
            except Organization.DoesNotExist:
                raise Http404(_("Organization does not exist.")) from None
        else:
            base_template = "accounts/base.html"

        pytitionuser = get_session_user(self.request)
        context.update({"user": pytitionuser, "base_template": base_template})

        if org_petition:
            try:
                permissions = Permission.objects.get(
                    organization=org, user=pytitionuser
                )
            except Permission.DoesNotExist:
                raise Http404(
                    _(
                        "Internal error, cannot find your permissions attached to "
                        "this organization (%(orgname)s)."
                    )
                    % {"orgname": org.name}
                ) from None
            context.update({"org": org, "user_permissions": permissions})
        else:
            petitions = pytitionuser.petition_set.all()
            context.update({"petitions": petitions})

        if self.steps.current == "step3":
            context.update(self.get_cleaned_data_for_step("step1"))
            context.update(self.get_cleaned_data_for_step("step2"))
        return dict(context)
