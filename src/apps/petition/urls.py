from django.conf import settings
from django.urls import include, path, reverse_lazy
from django.views.generic import RedirectView

from apps.petitions import views as petitions_views

from . import views
from .forms import PytitionUserCreationForm
from .views import PetitionCreationWizard, PytitionUserCreateView

urlpatterns = [
    # index
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    # Petition
    path("<int:petition_id>/", views.detail, name="detail"),
    path(
        "<int:petition_id>/confirm/<confirmation_hash>", views.confirm, name="confirm"
    ),
    path(
        "<int:petition_id>/get_csv_signature",
        views.get_csv_signature,
        {"only_confirmed": False},
        name="get_csv_signature",
    ),
    path(
        "<int:petition_id>/get_csv_confirmed_signature",
        views.get_csv_signature,
        {"only_confirmed": True},
        name="get_csv_confirmed_signature",
    ),
    path(
        "resend/<int:signature_id>",
        views.go_send_confirmation_email,
        name="resend_confirmation_email",
    ),
    path("<int:petition_id>/sign", views.create_signature, name="create_signature"),
    path(
        "<int:petition_id>/show_signatures",
        views.show_signatures,
        name="show_signatures",
    ),
    path(
        "<int:petition_id>/show_sympa_subscribe_bloc",
        views.show_sympa_subscribe_bloc,
        name="show_sympa_subscribe_bloc",
    ),
    path("<int:petition_id>/delete", views.petition_delete, name="petition_delete"),
    path("<int:petition_id>/publish", views.petition_publish, name="petition_publish"),
    path(
        "<int:petition_id>/unpublish",
        views.petition_unpublish,
        name="petition_unpublish",
    ),
    path("<int:petition_id>/edit", views.edit_petition, name="edit_petition"),
    path("<int:petition_id>/add_new_slug", views.add_new_slug, name="add_new_slug"),
    path("<int:petition_id>/del_slug", views.del_slug, name="del_slug"),
    path(
        "<int:petition_id>/report/<int:reason_id>",
        views.report_petition,
        name="report_petition",
    ),
    path("<int:petition_id>/report/", views.report_petition, name="report_petition"),
    path(
        "all_petitions",
        RedirectView.as_view(pattern_name="index", permanent=False),
        name="all_petitions",
    ),
    path(
        "transfer_petition/<int:petition_id>",
        views.transfer_petition,
        name="transfer_petition",
    ),
    # ──────────────────────────────────────────────────────────────────────────────────
    # Organization
    # ──────────────────────────────────────────────────────────────────────────────────
    path("org/", include("apps.organizations.urls", namespace="org")),
    # PUBLIC: show a petition by slug — org owner
    path(
        "org/<orgslugname>/<slug:petitionname>",
        petitions_views.slug_show_petition,
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
    path("user/new_template", petitions_views.new_template, name="user_new_template"),
    path("user/<user_name>", views.user_profile, name="user_profile"),
    path(
        "user/<username>/<slug:petitionname>",
        petitions_views.slug_show_petition,
        name="slug_show_petition",
    ),
    # Actions
    path("get_user_list", views.get_user_list, name="get_user_list"),
    path(
        "search_users_and_orgs",
        views.search_users_and_orgs,
        name="search_users_and_orgs",
    ),
    # Wizard
    path(
        "wizard/org/<slug:orgslugname>/new_petition",
        PetitionCreationWizard.as_view(views.WizardForms),
        name="org_petition_wizard",
    ),
    path(
        "wizard/org/<slug:orgslugname>/new_petition/from_template/<int:template_id>",
        PetitionCreationWizard.as_view(views.WizardForms),
        name="org_petition_wizard_from_template",
    ),
    path(
        "wizard/user/new_petition",
        PetitionCreationWizard.as_view(views.WizardForms),
        name="user_petition_wizard",
    ),
    path(
        "wizard/user/new_petition/from_template/<template_id>",
        PetitionCreationWizard.as_view(views.WizardForms),
        name="user_petition_wizard_from_template",
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
