"""pytition URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
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
from django.urls import include, re_path, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from apps.petition.views import index
from django.views.generic import RedirectView

urlpatterns = [
    re_path(r'^$', index, name="index"),
    re_path(r'^petition/', include('apps.petition.urls')),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^tinymce/', include('tinymce.urls')),
    re_path(r'^i18n/', include('django.conf.urls.i18n')),
    re_path(r'^maintenance-mode/', include('maintenance_mode.urls')),
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

favicon_urlpatterns = [
    path(f"{fname}", RedirectView.as_view(url=settings.STATIC_URL + fname, permanent=True))
    for fname in favicons
]

urlpatterns += favicon_urlpatterns
# Only in development: serve media and static files through Django.
# In production, these should be served by the web server (e.g. nginx).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)