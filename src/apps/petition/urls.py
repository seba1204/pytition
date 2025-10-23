from django.conf import settings
from django.urls import include, path, reverse_lazy

from apps.accounts.forms import PytitionUserCreationForm
from apps.consents.routes import NAMESPACE as CONSENT_NS
from apps.organizations.routes import NAMESPACE as ORG_NS
from apps.petition import views
from apps.petition.views import PytitionUserCreateView
from apps.petitions import forms as PF
from apps.petitions import views as PV
from apps.petitions.routes import NAMESPACE as PET_NS
from apps.signatures import views as SV

urlpatterns = [
    # index
    path("", views.index, name="index"),
    path("", include("apps.consents.urls", namespace=CONSENT_NS)),
    path("", include("apps.petitions.urls", namespace=PET_NS)),
    path("search", views.search, name="search"),
    # ──────────────────────────────────────────────────────────────────────────────────
    # Consents
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
    path("<int:petition_id>/report/", views.report_petition, name="report_petition"),
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
    # ──────────────────────────────────────────────────────────────────────────────────
    # Templates
    # ──────────────────────────────────────────────────────────────────────────────────
    path("templates/<int:template_id>/edit", views.edit_template, name="edit_template"),
    path(
        "templates/<int:template_id>/fav",
        views.template_fav_toggle,
        name="template_fav_toggle",
    ),
    path(
        "templates/<int:template_id>/delete",
        views.template_delete,
        name="template_delete",
    ),
    # User
    path("user/dashboard", views.user_dashboard, name="user_dashboard"),
    # TODO: move to theming app
    path("user/new_template", PV.new_template, name="user_new_template"),
    path("user/<user_name>", views.user_profile, name="user_profile"),
    path(
        "user/<username>/<slug:petitionname>",
        PV.slug_show_petition,
        name="slug_show_petition",
    ),
    # Actions
    path("get_user_list", views.get_user_list, name="get_user_list"),
    path(
        "search_users_and_orgs",
        views.search_users_and_orgs,
        name="search_users_and_orgs",
    ),
    # Authentication
    path("", include("django.contrib.auth.urls")),
    path("account_settings", views.account_settings, name="account_settings"),
    # Misc
    path("image_upload", views.image_upload, name="image_upload"),
]

if settings.ALLOW_REGISTER:
    urlpatterns += [
        path(
            "register/",
            PytitionUserCreateView.as_view(
                template_name="registration/register.html",
                form_class=PytitionUserCreationForm,
                success_url=reverse_lazy("login"),
            ),
            name="register",
        ),
    ]
