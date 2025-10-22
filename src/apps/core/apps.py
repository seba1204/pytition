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


class CoreConfig(AppConfig):
    name = "apps.core"
    verbose_name = "Pytition Core Utilities"
