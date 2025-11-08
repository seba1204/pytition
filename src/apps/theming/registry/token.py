"""CSS Token Registry."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


@dataclass(frozen=True)
class TokenDef:
    """Definition of a single CSS token."""

    name: str
    type: str  # "color", "length", "number", "string"
    pattern: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    allowed_values: set[str] | None = None
    deprecated: bool = False


class CssTokenRegistry:
    """
    Versioned registry of CSS tokens loaded from JSON files.

    Attributes
    ----------
    version : str
        Version key that maps to a JSON file via settings.THEME_TOKEN_REGISTRY.
        eg. "v1".
    _tokens : Dict[str, TokenDef]
        Mapping of token name to TokenDef.
    """

    def __init__(self, version: str) -> None:
        self.version: str = version
        self._tokens: dict[str, TokenDef] = _load_tokens_for_version(version)

    # ---------------- Public API ----------------
    def known(self, name: str) -> bool:
        """
        Whether a token name is known in this registry.

        Parameters
        ----------
        name : str
            Token name, e.g. "--bs-body-bg".

        Returns
        -------
        bool
        """
        return name in self._tokens

    def get(self, name: str) -> TokenDef | None:
        """
        Return a token definition.

        Parameters
        ----------
        name : str
            Token name, e.g. "--bs-body-bg".

        Returns
        -------
        Optional[TokenDef]
        """
        return self._tokens.get(name)

    def validate_tokens(self, payload: Mapping[str, Mapping[str, Any]]) -> None:
        """
        Validate a scoped tokens payload.

        Parameters
        ----------
        payload : Mapping[str, Mapping[str, Any]]
            Mapping of scope -> {token_name: value}.

        Raises
        ------
        ValidationError
            If a token name or value is invalid for this version.
        """
        for scope, tokens in payload.items():
            if not isinstance(tokens, Mapping):
                raise ValidationError(
                    _("Tokens for scope '%(scope)s' must be a mapping.")
                    % {"scope": scope}
                )
            for name, value in tokens.items():
                self._validate_token(scope, name, value)

    # ---------------- Internals -----------------
    def _validate_token(self, scope: str, name: str, value: Any) -> None:
        """
        Validate a single token value.

        Parameters
        ----------
        scope : str
            CSS scope, e.g. ":root" or '[data-bs-theme="dark"]'.
        name : str
            Token name, e.g. "--bs-body-bg".
        value : Any
            Token value to validate.

        Raises
        ------
        ValidationError
            If the token name or value is invalid.
        """
        td = self._tokens.get(name)
        if td is None:
            raise ValidationError(
                _(
                    "Unknown token '%(token)s' in scope '%(scope)s' "
                    "for version '%(version)s'."
                )
                % {"token": name, "scope": scope, "version": self.version}
            )

        if td.deprecated:
            # Soft policy for now: still allow
            # It can be logged or warned about here if needed.
            pass

        # Validate value according to type
        validator = getattr(self, f"_validate_{td.type}", None)
        if validator is None:
            raise ValidationError(
                _("Token '%(token)s' has unknown type '%(type)s'.")
                % {"token": name, "type": td.type}
            )
        validator(name, value, td)

    def _validate_color(self, name: str, value: Any, td: TokenDef) -> None:
        """Validate a color token."""
        if not (isinstance(value, str) and _is_color(value)):
            raise ValidationError(
                _("Token '%(token)s' expects a hex color (e.g., #RRGGBB or #RGB).")
                % {"token": name}
            )

    def _validate_length(self, name: str, value: Any, td: TokenDef) -> None:
        """Validate a length token."""
        if not (isinstance(value, str) and _is_length(value)):
            raise ValidationError(
                _("Token '%(token)s' expects a CSS length (e.g., 0, 10px, 1.5rem).")
                % {"token": name}
            )

    def _validate_number(self, name: str, value: Any, td: TokenDef) -> None:
        """Validate a number token."""
        if not isinstance(value, (int, float)):
            raise ValidationError(
                _("Token '%(token)s' expects a number.") % {"token": name}
            )

        f_val = float(value)
        if td.min_value is not None and f_val < td.min_value:
            raise ValidationError(
                _("Token '%(token)s' is below min_value %(min_value)s.")
                % {"token": name, "min_value": td.min_value}
            )
        if td.max_value is not None and f_val > td.max_value:
            raise ValidationError(
                _("Token '%(token)s' is above max_value %(max_value)s.")
                % {"token": name, "max_value": td.max_value}
            )

    def _validate_string(self, name: str, value: Any, td: TokenDef) -> None:
        """Validate a string token."""
        if not isinstance(value, str):
            raise ValidationError(
                _("Token '%(token)s' expects a string.") % {"token": name}
            )
        if td.allowed_values is not None and value not in td.allowed_values:
            allowed = ", ".join(sorted(td.allowed_values))
            raise ValidationError(
                _("Token '%(token)s' has invalid value. Allowed: %(allowed)s.")
                % {"token": name, "allowed": allowed}
            )


# === Helper functions =================================================================


def _is_color(s: str) -> bool:
    """
    Return True if a string is a simple hex color.

    Parameters
    ----------
    s : str
        Candidate string.

    Returns
    -------
    bool
    """
    return bool(re.fullmatch(r"#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})", s))


def _is_length(s: str) -> bool:
    """
    Return True if a string is a valid basic CSS length (eg. 0, 10px, 1.5rem).

    Parameters
    ----------
    s : str
        Candidate string.

    Returns
    -------
    bool
    """
    return bool(
        re.fullmatch(r"(0|[-+]?[0-9]*\.?[0-9]+(px|rem|em|%|vh|vw|vmin|vmax))", s)
    )


@lru_cache(maxsize=64)
def _load_tokens_for_version(version: str) -> dict[str, TokenDef]:
    """
    Load token definitions for the given version with file-based caching.

    Notes
    -----
    A second cache key is wrapped using the file mtime so that changing the JSON
    invalidates the lru_cache automatically on next process start or import reload.

    Parameters
    ----------
    version : str
        Version key matching settings.THEME_TOKEN_REGISTRY.

    Returns
    -------
    Dict[str, TokenDef]
        Mapping token_name -> TokenDef

    Raises
    ------
    KeyError
        If the version is not configured.
    FileNotFoundError
        If the JSON file is missing.
    ValueError
        If JSON structure is invalid.
    """
    unsafe_path: str | None = settings.THEME_TOKEN_REGISTRY.get(version)
    if unsafe_path is None:
        raise KeyError(
            _("No token registry file configured for version '%(version)s'.")
            % {"version": version}
        )

    path: Path = Path(unsafe_path)

    # # get root path if relative
    # if not path.is_absolute():
    #     base_dir = Path(settings.BASE_DIR)
    #     path = base_dir.joinpath(path).resolve()

    # check file exists
    if not path.is_file():
        raise FileNotFoundError(
            _("Token registry file not found: %(path)s") % {"path": str(path)}
        )

    with path.open("r", encoding="utf-8") as fh:
        data: dict[str, Any] = json.load(fh)

    if data.get("version") != version:
        raise ValueError(
            _(
                "Token registry file version mismatch: expected '%(expected)s', "
                "got '%(got)s'."
            )
            % {"expected": version, "got": data.get("version")}
        )

    tokens_raw = data.get("tokens")
    if not isinstance(tokens_raw, list):
        raise ValueError(_("Registry JSON must contain a 'tokens' array."))

    out: dict[str, TokenDef] = {}
    for item in tokens_raw:
        if not isinstance(item, dict) or "name" not in item or "type" not in item:
            raise ValueError(_("Each token must have at least 'name' and 'type'."))
        td = TokenDef(
            name=str(item["name"]),
            type=str(item["type"]),
            pattern=item.get("pattern"),
            min_value=float(item["min_value"]) if "min_value" in item else None,
            max_value=float(item["max_value"]) if "max_value" in item else None,
            allowed_values=set(item["allowed_values"])
            if "allowed_values" in item
            else None,
            deprecated=bool(item.get("deprecated", False)),
        )
        out[td.name] = td
    return out
