"""
Pytition URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/

Examples
--------
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.urls.resolvers import URLPattern, URLResolver
from django.views.generic import RedirectView

from apps.accounts.routes import NAMESPACE as ACCOUNT_NS
from apps.consents.routes import NAMESPACE as CONSENT_NS
from apps.core import views as CV
from apps.core.routes import SEARCH_NS
from apps.core.views import index
from apps.files.routes import NAMESPACE as FILES_NS
from apps.moderation.routes import NAMESPACE as MOD_NS
from apps.organizations.routes import NAMESPACE as ORG_NS
from apps.petitions import views as PV
from apps.petitions.routes import NAMESPACE as PET_NS
from apps.presets.routes import NAMESPACE as PRESET_NS
from apps.signatures.routes import NAMESPACE as SIGN_NS

urlpatterns: list[URLPattern | URLResolver]

PID = "<int:petition_id>"

urlpatterns = [
    path("", index, name="index"),
    path("admin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("django.contrib.auth.urls")),
    # Maintenance mode URLs (3rd party app)
    path("maintenance-mode/", include("maintenance_mode.urls")),
    path("", CV.index, name="index"),
    path("files/", include("apps.files.urls", namespace=FILES_NS)),
    path("moderation/", include("apps.moderation.urls", namespace=MOD_NS)),
    path("org/", include("apps.organizations.urls", namespace=ORG_NS)),
    path("presets/", include("apps.presets.urls", namespace=PRESET_NS)),
    path("search/", include("apps.core.urls.search", namespace=SEARCH_NS)),
    path("user/", include("apps.accounts.urls", namespace=ACCOUNT_NS)),
    path(f"p/{PID}/consents/", include("apps.consents.urls", namespace=CONSENT_NS)),
    path(f"p/{PID}/signatures/", include("apps.signatures.urls", namespace=SIGN_NS)),
    path("p/", include("apps.petitions.urls", namespace=PET_NS)),
    # ──────────────────────────────────────────────────────────────────────────────────
    # LEGACY: show a petition by its owner (user/org)
    # ──────────────────────────────────────────────────────────────────────────────────
    path(
        "petition/org/<orgslugname>/<slug:petitionname>",
        PV.slug_show_petition,
        name="slug_show_petition",
    ),
    path(
        "petition/user/<username>/<slug:petitionname>",
        PV.slug_show_petition,
        name="slug_show_petition",
    ),
]


# Favicons & manifest from static files:
favicons = [
    "favicon.ico",
    "favicon-16x16.png",
    "favicon-32x32.png",
    "favicon-48x48.png",
    "apple-touch-icon.png",
    "android-chrome-192x192.png",
    "android-chrome-512x512.png",
    "mstile-150x150.png",
    "safari-pinned-tab.svg",
    "manifest.json",
    "site.webmanifest",
    "browserconfig.xml",
]

# Generate URL patterns for each favicon to serve them from the static files location.
favicon_urlpatterns: list[URLPattern] = [
    path(
        f"{fname}",
        RedirectView.as_view(url=settings.STATIC_URL + fname, permanent=True),
    )
    for fname in favicons
]

urlpatterns += favicon_urlpatterns
# Only in development: serve media and static files through Django.
# In production, these should be served by the web server (e.g. nginx).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
