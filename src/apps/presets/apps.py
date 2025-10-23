"""
Petition presets management.

A petition presets allow users to create new petition templates that can be reused for
creating petitions quickly.

Each user and org get a special preset which is the default one.
"""

from django.apps import AppConfig


class PresetsConfig(AppConfig):
    name = "apps.presets"
