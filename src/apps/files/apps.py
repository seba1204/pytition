from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _lazy


class FilesConfig(AppConfig):
    name = "apps.files"
    # Translators: Files application verbose name (in the admin interface)
    verbose_name = _lazy("Files Management")
