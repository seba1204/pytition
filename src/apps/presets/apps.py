"""
Petition presets management.

A petition presets allow users to create new petition templates that can be reused for
creating petitions quickly.

Use cases:

- An national org create specific presets for its local branches.
- Setting up a specific SMTP config for mail sending from a specific mail address.
- Basically, all complex configuration that you want to do only once.

Each user and organization get a special preset which is the default one.
"""

from django.apps import AppConfig


class PresetsConfig(AppConfig):
    name = "apps.presets"
