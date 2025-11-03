"""
Project-wide utilities and shared glue.

Hosts cross-cutting pieces such as middleware, base views, and helpers that
do not belong to a specific business domain.

Notes
-----
- Avoid domain-specific logic here; depend downwards on domain apps if needed.
- Keep this app small to prevent becoming a new "mega app".
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _lazy


class CoreConfig(AppConfig):
    name = "apps.core"
    # Translators: Core application verbose name (in the admin interface)
    verbose_name = _lazy("Core Application")
