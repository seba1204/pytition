"""Common utilities for theming tests."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any, Final
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model

from apps.accounts.models import PytitionUser
from apps.organizations.models import Organization

_UNIQ_PREFIX: Final[str] = "test_"


class RegistrySettingsMixin(unittest.TestCase):
    """
    Mixin that prepares a temporary versioned token registry and overrides settings.

    Notes
    -----
    - Creates v1.json and v2.json in a temp folder.
    - Overrides THEME_TOKEN_REGISTRY and THEME_ALLOWED_TOKEN_SCOPES.
    """

    _tmpdir: Path
    _saved_registry: dict[str, Any]
    _saved_scopes: set[str]

    @classmethod
    def setUpClass(cls) -> None:
        """Set up temporary token registry and override settings."""
        super().setUpClass()
        cls._tmpdir = Path(tempfile.mkdtemp(prefix="theme_tokens_"))

        (cls._tmpdir / "v1.json").write_text(
            json.dumps(
                {
                    "version": "v1",
                    "tokens": [
                        {"name": "--bs-body-bg", "type": "color"},
                        {"name": "--bs-border-radius", "type": "length"},
                    ],
                }
            ),
            encoding="utf-8",
        )
        (cls._tmpdir / "v2.json").write_text(
            json.dumps(
                {
                    "version": "v2",
                    "tokens": [
                        {"name": "--bs-body-bg", "type": "color"},
                        {"name": "--bs-border-radius", "type": "length"},
                        {"name": "--bs-body-font-size", "type": "length"},
                    ],
                }
            ),
            encoding="utf-8",
        )

        cls._saved_registry = dict(getattr(settings, "THEME_TOKEN_REGISTRY", {}))
        cls._saved_scopes = set(
            getattr(settings, "THEME_ALLOWED_TOKEN_SCOPES", {":root"})
        )
        settings.THEME_TOKEN_REGISTRY = {
            "v1": cls._tmpdir / "v1.json",
            "v2": cls._tmpdir / "v2.json",
        }
        settings.THEME_ALLOWED_TOKEN_SCOPES = {
            ":root",
            '[data-bs-theme="dark"]',
        }

    @classmethod
    def tearDownClass(cls) -> None:
        """Restore settings and clean up temporary files."""
        try:
            settings.THEME_TOKEN_REGISTRY = cls._saved_registry
            settings.THEME_ALLOWED_TOKEN_SCOPES = cls._saved_scopes
        finally:
            shutil.rmtree(cls._tmpdir, ignore_errors=True)
            super().tearDownClass()


def make_pytition_user(username: str | None = None) -> PytitionUser:
    """
    Return a PytitionUser linked to AUTH_USER_MODEL, resilient to post_save signals.

    Parameters
    ----------
    username : str | None
        Desired username; if None, a unique username is generated.

    Returns
    -------
    PytitionUser
        Persisted instance.
        If a post_save signal already created it, the existing one is returned.
    """
    BaseUser = get_user_model()
    uname = username or f"{_UNIQ_PREFIX}{uuid4().hex[:8]}"
    auth_user = BaseUser.objects.create_user(username=uname, password="x")

    # If a post_save signal already created the related PytitionUser, reuse it.
    try:
        return auth_user.pytitionuser  # created by signal
    except PytitionUser.DoesNotExist:
        # should not happen
        return PytitionUser.objects.create(user=auth_user)


def make_org(slug: str | None = None, name: str | None = None) -> Organization:
    """
    Create and return an Organization with given or generated slug and name.

    Parameters
    ----------
    slug : str | None
        Desired slug; if None, a unique slug is generated.
    name : str | None
        Desired name; if None, a name based on the slug is generated.

    Returns
    -------
    Organization
        Persisted instance.
    """
    slug = slug or f"org-{uuid4().hex[:6]}"
    name = name or f"Org {slug}"
    return Organization.objects.create(name=name)


def compact_css(css: str) -> str:
    """
    Return a minified version of the given CSS string for easier comparison.

    Parameters
    ----------
    css : str
        Raw CSS string.

    Returns
    -------
    str
        Minified CSS string.
    """
    return "".join(
        line.strip().replace(" ", "") for line in css.splitlines() if line.strip()
    )
