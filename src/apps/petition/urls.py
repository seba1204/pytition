from django.urls import include, path

from apps.accounts import views as AV
from apps.accounts.routes import NAMESPACE as ACCOUNT_NS
from apps.consents.routes import NAMESPACE as CONSENT_NS
from apps.core import views as CV
from apps.files.routes import NAMESPACE as MEDIA_NS
from apps.moderation import views as MV
from apps.organizations.routes import NAMESPACE as ORG_NS
from apps.petitions import forms as PF
from apps.petitions import views as PV
from apps.petitions.routes import NAMESPACE as PET_NS
from apps.presets.routes import NAMESPACE as PRESET_NS
from apps.signatures import views as SV

urlpatterns = [
    # index
    path("", CV.index, name="index"),
    path("", include("apps.consents.urls", namespace=CONSENT_NS)),
    path("", include("apps.petitions.urls", namespace=PET_NS)),
    path("user/", include("apps.accounts.urls", namespace=ACCOUNT_NS)),
    path("presets/", include("apps.presets.urls", namespace=PRESET_NS)),
    path("media/", include("apps.files.urls", namespace=MEDIA_NS)),
    # ──────────────────────────────────────────────────────────────────────────────────
    # Search, will be improved, cf. ticket #20
    # ──────────────────────────────────────────────────────────────────────────────────
    path("search", CV.search, name="search"),
    path(
        "search_users_and_orgs",
        CV.search_profiles,
        name="search_users_and_orgs",
    ),
    path("get_user_list", AV.user_list, name="get_user_list"),
    # ──────────────────────────────────────────────────────────────────────────────────
    # Signatures # TODO: move it to an urls.py so it can be included
    # ──────────────────────────────────────────────────────────────────────────────────
    path(
        "<int:petition_id>/get_csv_signature",
        SV.get_csv_signature,
        {"only_confirmed": False},
        name="get_csv_signature",
    ),
    path(
        "<int:petition_id>/get_csv_confirmed_signature",
        SV.get_csv_signature,
        {"only_confirmed": True},
        name="get_csv_confirmed_signature",
    ),
    path(
        "<int:petition_id>/sign",
        SV.create,
        name="create_signature",
    ),
    path(
        "<int:petition_id>/show_signatures",
        SV.show_signatures,
        name="show_signatures",
    ),
    # ──────────────────────────────────────────────────────────────────────────────────
    # Petitions
    # ──────────────────────────────────────────────────────────────────────────────────
    # Wizard : TODO: for now it stay here, but will be deleted
    path(
        "wizard/org/<slug:orgslugname>/new_petition",
        PF.PetitionCreationWizard.as_view(PF.WizardForms),
        name="org_petition_wizard",
    ),
    path(
        "wizard/org/<slug:orgslugname>/new_petition/from_template/<int:template_id>",
        PF.PetitionCreationWizard.as_view(PF.WizardForms),
        name="org_petition_wizard_from_template",
    ),
    path(
        "wizard/user/new_petition",
        PF.PetitionCreationWizard.as_view(PF.WizardForms),
        name="user_petition_wizard",
    ),
    path(
        "wizard/user/new_petition/from_template/<template_id>",
        PF.PetitionCreationWizard.as_view(PF.WizardForms),
        name="user_petition_wizard_from_template",
    ),
    # ──────────────────────────────────────────────────────────────────────────────────
    # Moderation
    # ──────────────────────────────────────────────────────────────────────────────────
    path("<int:petition_id>/report/", MV.report, name="report_petition"),
    # ──────────────────────────────────────────────────────────────────────────────────
    # Organization
    # ──────────────────────────────────────────────────────────────────────────────────
    path("org/", include("apps.organizations.urls", namespace=ORG_NS)),
    # PUBLIC: show a petition by slug — org owner
    path(
        "org/<orgslugname>/<slug:petitionname>",
        PV.slug_show_petition,
        name="slug_show_petition",
    ),
    path(
        "user/<username>/<slug:petitionname>",
        PV.slug_show_petition,
        name="slug_show_petition",
    ),
    # ──────────────────────────────────────────────────────────────────────────────────
    # Django built-in views
    # ──────────────────────────────────────────────────────────────────────────────────
    # Authentication
    path("", include("django.contrib.auth.urls")),
]
