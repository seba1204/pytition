"""Module for organization app URLs."""

from django.urls import path
from django.urls.resolvers import URLPattern

from apps.organizations import views
from apps.petitions import views as petitions_views

app_name = "organizations"
urlpatterns: list[URLPattern] = [
    path("create", views.org_create, name="create"),
    path("<slug:orgslugname>", views.org_profile, name="profile"),
    path(
        "<slug:orgslugname>/dashboard",
        views.org_dashboard,
        name="dashboard",
    ),
    path("<slug:orgslugname>/leave_org", views.leave_org, name="leave"),
    path("<slug:orgslugname>/add_user", views.org_add_user, name="add_user"),
    path(
        "<slug:orgslugname>/new_template",
        petitions_views.new_template,
        name="new_template",
    ),
    path(
        "<slug:orgslugname>/delete_member",
        views.org_delete_member,
        name="delete_member",
    ),
    path(
        "<slug:orgslugname>/invite_accept",
        views.invite_accept,
        name="invite_accept",
    ),
    path(
        "<slug:orgslugname>/invite_dismiss",
        views.invite_dismiss,
        name="invite_dismiss",
    ),
    path(
        "<slug:orgslugname>/edit_user_permissions/<user_name>",
        views.org_edit_user_perms,
        name="edit_user_perms",
    ),
    path(
        "<slug:orgslugname>/set_user_permissions/<user_name>",
        views.org_set_user_perms,
        name="set_user_perms",
    ),
    path(
        "<slug:orgslugname>/<slug:petitionname>",
        petitions_views.slug_show_petition,
        name="slug_show_petition",
    ),
]
