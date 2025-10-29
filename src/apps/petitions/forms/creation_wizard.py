from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from formtools.wizard.views import SessionWizardView  # type: ignore

from apps.accounts.routes import AccountsRoute
from apps.accounts.services import get_session_user
from apps.organizations.routes import OrgRoute
from apps.petition.models import Organization, Permission, Petition, PetitionTemplate
from apps.petitions.routes import PetitionsRoute

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
    "step1": "petition/new_petition_step1.html",
    "step2": "petition/new_petition_step2.html",
    "step3": "petition/new_petition_step3.html",
}


# Class Based Controller
# PATH : subroutes of /wizard
@method_decorator(login_required, name="dispatch")
class PetitionCreationWizard(SessionWizardView):
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if settings.DISABLE_USER_PETITION and "orgslugname" not in self.kwargs:
            messages.error(
                request, _("Users are not allowed to create their own petitions.")
            )
            return redirect(AccountsRoute.DASHBOARD)
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self) -> list[str]:
        return [WizardTemplates[self.steps.current]]

    def get_form_initial(self, step: str) -> dict[str, Any]:
        template = None
        org_petition = "orgslugname" in self.kwargs
        if org_petition:
            orgslugname = self.kwargs["orgslugname"]
            org = Organization.objects.get(slugname=orgslugname)
        else:
            pytitionuser = get_session_user(self.request)

        # Get the template, if any
        if "template_id" in self.kwargs:
            template = PetitionTemplate.objects.get(pk=self.kwargs["template_id"])
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
        if step == "step1":
            org_petition = "orgslugname" in self.kwargs
            if org_petition:
                orgslugname = self.kwargs["orgslugname"]
                kwargs = {"orgslugname": orgslugname}
            else:
                pytitionuser = get_session_user(self.request)
                kwargs = {"user_name": pytitionuser.user.username}
            return kwargs
        else:
            return {}

    # FIXME: this method is too long, split it into smaller methods
    def done(self, form_list: list[Any], **kwargs: Any) -> HttpResponse:  # noqa
        org_petition = "orgslugname" in self.kwargs
        title = self.get_cleaned_data_for_step("step1")["title"]
        message = self.get_cleaned_data_for_step("step2")["message"]
        publish = self.get_cleaned_data_for_step("step3")["publish"]
        template_id = self.get_cleaned_data_for_step("step3")["template_id"]
        use_template = self.get_cleaned_data_for_step("step3")["use_template"]
        pytitionuser = get_session_user(self.request)
        _redirect = self.request.POST.get("redirect", "")

        if org_petition:
            orgslugname = self.kwargs["orgslugname"]
            try:
                org = Organization.objects.get(slugname=orgslugname)
            except Organization.DoesNotExist:
                messages.error(self.request, _("Cannot find this organization"))
                return redirect(AccountsRoute.DASHBOARD)

            try:
                permissions = Permission.objects.get(
                    organization=org, user=pytitionuser
                )
            except Permission.DoesNotExist:
                return redirect(OrgRoute.DASHBOARD, orgslugname)

            if pytitionuser in org.members.all() and permissions.can_create_petitions:
                # FIXME I think new here is better than create
                petition = Petition.objects.create(title=title, text=message, org=org)
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
                            _("This template does not belong to your organization"),
                        )
                        return redirect(OrgRoute.DASHBOARD, orgslugname)
                if publish:
                    petition.publish()
                if _redirect and _redirect == "1":
                    return redirect(PetitionsRoute.EDIT, petition.id)
                else:
                    return redirect(OrgRoute.DASHBOARD, orgslugname)
            else:
                messages.error(
                    self.request,
                    _(
                        "You don't have the permission to create a new petition in "
                        "this Organization"
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
                        self.request, _("This template does not belong to you")
                    )
                    return redirect(AccountsRoute.DASHBOARD)
            if publish:
                petition.publish()
            if _redirect and _redirect == "1":
                return redirect(PetitionsRoute.EDIT, petition.id)
            else:
                return redirect(AccountsRoute.DASHBOARD)

    def get_context_data(self, form: Any, **kwargs: Any) -> dict[str, Any]:
        org_petition = "orgslugname" in self.kwargs
        context = super().get_context_data(form=form, **kwargs)
        if org_petition:
            base_template = "org/base.html"
            try:
                org = Organization.objects.get(slugname=self.kwargs["orgslugname"])
            except Organization.DoesNotExist:
                raise Http404(_("Organization does not exist")) from None
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
                        "this organization ('{orgname}')".format(orgname=org.name)
                    )
                ) from None
            context.update({"org": org, "user_permissions": permissions})
        else:
            petitions = pytitionuser.petition_set.all()
            context.update({"petitions": petitions})

        if self.steps.current == "step3":
            context.update(self.get_cleaned_data_for_step("step1"))
            context.update(self.get_cleaned_data_for_step("step2"))
        return dict(context)
