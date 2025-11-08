"""Tests for JSON registry loading and scope validation."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from apps.theming.models import Theme
from apps.theming.registry.token import CssTokenRegistry
from apps.theming.tests.common import RegistrySettingsMixin, make_pytition_user


class RegistryValidationTests(RegistrySettingsMixin, TestCase):
    """Tests for JSON registry loading and scope validation."""

    @staticmethod
    def _write_registry(tmpdir: Path, name: str, payload: dict[str, Any]) -> str:
        """
        Create a registry JSON file.

        Parameters
        ----------
        tmpdir : Path
            Temporary directory where to write the JSON file.
        name : str
            Base file name without extension.
        payload : dict
            JSON payload to dump.

        Returns
        -------
        str
            Absolute path to the written JSON file.
        """
        path = tmpdir / f"{name}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return str(path)

    def test_loader_errors_when_scopes_missing(self) -> None:
        """Registry must define a 'scopes' array."""
        with tempfile.TemporaryDirectory(prefix="registry_") as d:
            tmp = Path(d)
            v1 = self._write_registry(
                tmp,
                "v1",
                {
                    "version": "v1",
                    "tokens": [{"name": "--x", "type": "color"}],
                    # "scopes" intentionally missing
                },
            )
            reg_map = {"v1": v1}

            with (
                override_settings(THEME_TOKEN_REGISTRY=reg_map),
                self.assertRaises(ValidationError) as ctx,
            ):
                CssTokenRegistry("v1")  # loading happens in __init__

        self.assertIn("scopes", str(ctx.exception).lower())
        self.assertIn("array of strings", str(ctx.exception).lower())

    def test_loader_errors_when_scopes_is_not_list_of_strings(self) -> None:
        """Registry 'scopes' must be a list[str]."""
        with tempfile.TemporaryDirectory(prefix="registry_") as d:
            tmp = Path(d)
            v1 = self._write_registry(
                tmp,
                "v1",
                {
                    "version": "v1",
                    "tokens": [{"name": "--x", "type": "color"}],
                    "scopes": [":root", 123],  # invalid: not all strings
                },
            )
            reg_map = {"v1": v1}

            with (
                override_settings(THEME_TOKEN_REGISTRY=reg_map),
                self.assertRaises(ValidationError) as ctx,
            ):
                CssTokenRegistry("v1")

        self.assertIn("scopes", str(ctx.exception).lower())
        self.assertIn("array of strings", str(ctx.exception).lower())

    def test_loader_errors_on_version_mismatch(self) -> None:
        """Registry 'version' field must match the mapping key."""
        with tempfile.TemporaryDirectory(prefix="registry_") as d:
            tmp = Path(d)
            # File says v2, but we will map it under key 'v1' on purpose.
            bad = self._write_registry(
                tmp,
                "weird",
                {
                    "version": "v2",
                    "tokens": [{"name": "--x", "type": "color"}],
                    "scopes": [":root"],
                },
            )
            reg_map = {"v1": bad}

            with (
                override_settings(THEME_TOKEN_REGISTRY=reg_map),
                self.assertRaises(ValidationError) as ctx,
            ):
                CssTokenRegistry("v1")

        self.assertIn("version", str(ctx.exception).lower())
        self.assertIn("mismatch", str(ctx.exception).lower())

    def test_loader_errors_when_tokens_not_array(self) -> None:
        """Registry 'tokens' must be an array."""
        with tempfile.TemporaryDirectory(prefix="registry_") as d:
            tmp = Path(d)
            v1 = self._write_registry(
                tmp,
                "v1",
                {
                    "version": "v1",
                    "tokens": {"not": "a list"},  # invalid
                    "scopes": [":root"],
                },
            )
            reg_map = {"v1": v1}

            with (
                override_settings(THEME_TOKEN_REGISTRY=reg_map),
                self.assertRaises(ValidationError) as ctx,
            ):
                CssTokenRegistry("v1")

        self.assertIn("tokens", str(ctx.exception).lower())
        self.assertIn("array", str(ctx.exception).lower())

    def test_validate_tokens_rejects_unknown_scope(self) -> None:
        """Theme.clean() should raise when tokens_css contains an unknown scope."""
        creator = make_pytition_user("creator")
        p_user = make_pytition_user("ok-owner")
        with tempfile.TemporaryDirectory(prefix="registry_") as d:
            tmp = Path(d)
            v1 = self._write_registry(
                tmp,
                "v1",
                {
                    "version": "v1",
                    "tokens": [{"name": "--bs-body-bg", "type": "color"}],
                    "scopes": [":root"],
                },
            )
            reg_map = {"v1": v1}

            with override_settings(THEME_TOKEN_REGISTRY=reg_map):
                t = Theme(
                    name="Ok",
                    creator=creator,
                    tokens_schema_version="v1",
                    tokens_css={"[data-unknown]": {"--bs-body-bg": "#ffffff"}},
                    components_css="/* empty */",
                )
                t.set_owner(p_user)
                with self.assertRaises(ValidationError) as ctx:
                    t.full_clean()

        msg = str(ctx.exception)
        self.assertIn("invalid token scopes", msg.lower())
        self.assertIn("[data-unknown]", msg)

    def test_validate_tokens_accepts_known_scope(self) -> None:
        """Theme.clean() should pass when tokens_css uses only allowed scopes."""
        creator = make_pytition_user("creator")
        with tempfile.TemporaryDirectory(prefix="registry_") as d:
            tmp = Path(d)
            v1 = self._write_registry(
                tmp,
                "v1",
                {
                    "version": "v1",
                    "tokens": [{"name": "--bs-body-bg", "type": "color"}],
                    "scopes": [":root"],
                },
            )
            reg_map = {"v1": v1}

            with override_settings(THEME_TOKEN_REGISTRY=reg_map):
                t = Theme(
                    name="Ok",
                    creator=creator,
                    tokens_schema_version="v1",
                    tokens_css={":root": {"--bs-body-bg": "#ffffff"}},
                )
                t.set_owner(creator)
                # Should not raise
                t.full_clean()
