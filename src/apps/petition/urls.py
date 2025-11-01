from django.urls import include, path

from apps.accounts.routes import NAMESPACE as ACCOUNT_NS
from apps.consents.routes import NAMESPACE as CONSENT_NS
from apps.core import views as CV
from apps.core.routes import SEARCH_NS
from apps.files.routes import NAMESPACE as FILES_NS
from apps.moderation.routes import NAMESPACE as MOD_NS
from apps.organizations.routes import NAMESPACE as ORG_NS
from apps.petitions import forms as PF
from apps.petitions import views as PV
from apps.petitions.routes import NAMESPACE as PET_NS
from apps.presets.routes import NAMESPACE as PRESET_NS
from apps.signatures.routes import NAMESPACE as SIGN_NS

urlpatterns = [
    # index
    path("", CV.index, name="index"),
    path("", include("apps.consents.urls", namespace=CONSENT_NS)),
    path("", include("apps.petitions.urls", namespace=PET_NS)),
    path("files/", include("apps.files.urls", namespace=FILES_NS)),
    path("moderation/", include("apps.moderation.urls", namespace=MOD_NS)),
    path("org/", include("apps.organizations.urls", namespace=ORG_NS)),
    path("presets/", include("apps.presets.urls", namespace=PRESET_NS)),
    path("search/", include("apps.core.urls.search", namespace=SEARCH_NS)),
    path("user/", include("apps.accounts.urls", namespace=ACCOUNT_NS)),
    path(
        "<int:petition_id>/signatures/",
        include("apps.signatures.urls", namespace=SIGN_NS),
    ),
    # ──────────────────────────────────────────────────────────────────────────────────
    # Wizard
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
    # LEGACY: show a petition by slug through user/org name
    # ──────────────────────────────────────────────────────────────────────────────────
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
]
