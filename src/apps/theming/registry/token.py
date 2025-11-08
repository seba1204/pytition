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
    _allowed_scopes : set[str]
        Allowed CSS scopes provided by the registry JSON.
    """

    def __init__(self, version: str) -> None:
        self.version: str = version
        tokens, scopes = _load_registry_for_version(version)
        self._tokens: dict[str, TokenDef] = tokens
        self._allowed_scopes: set[str] = scopes

    # ---------------- Public API ----------------

    @property
    def allowed_scopes(self) -> set[str]:
        """Return the set of allowed scopes loaded from the registry JSON."""
        return set(self._allowed_scopes)

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
        # Validate scopes present in payload
        invalid_scopes = set(payload.keys()) - self._allowed_scopes
        if invalid_scopes:
            raise ValidationError(
                _("Invalid token scopes: %(scopes)s")
                % {"scopes": ", ".join(sorted(invalid_scopes))}
            )

        # Validate tokens per scope
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


def _load_registry_for_version(version: str) -> tuple[dict[str, TokenDef], set[str]]:
    """
    Load tokens and scopes for a given version from JSON.

    Parameters
    ----------
    version : str
        Schema version key (e.g. "v1").

    Returns
    -------
    (dict[str, TokenDef], set[str])
        Mapping token_name -> TokenDef, and the allowed scopes set.

    Raises
    ------
    FileNotFoundError
        If the JSON path is not found.
    ValidationError
        If the JSON is invalid or missing required keys.
    """
    mapping = getattr(settings, "THEME_TOKEN_REGISTRY", None)
    if not isinstance(mapping, Mapping) or version not in mapping:
        raise FileNotFoundError(f"No token registry mapping for version '{version}'")

    path = Path(mapping[version])
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, Mapping):
        raise ValidationError(_("Registry JSON must be a mapping."))

    if data.get("version") != version:
        raise ValidationError(_("Registry 'version' mismatch."))

    tokens_raw = data.get("tokens")
    if not isinstance(tokens_raw, list):
        raise ValidationError(_("Registry must contain a 'tokens' array."))

    scopes_raw = data.get("scopes")
    if not isinstance(scopes_raw, list) or not all(
        isinstance(s, str) for s in scopes_raw
    ):
        raise ValidationError(_("Registry must contain a 'scopes' array of strings."))

    tokens: dict[str, TokenDef] = {}
    for item in tokens_raw:
        if not isinstance(item, Mapping) or "name" not in item or "type" not in item:
            raise ValidationError(_("Each token must have at least 'name' and 'type'."))
        td = TokenDef(
            name=str(item["name"]),
            type=str(item["type"]),
            pattern=str(item["pattern"]) if "pattern" in item else None,
            min_value=float(item["min_value"]) if "min_value" in item else None,
            max_value=float(item["max_value"]) if "max_value" in item else None,
            allowed_values=set(item["allowed_values"])
            if "allowed_values" in item
            else None,
            deprecated=bool(item.get("deprecated", False)),
        )
        tokens[td.name] = td

    return tokens, set(scopes_raw)


@lru_cache(maxsize=32)
def _load_tokens_for_version(version: str) -> dict[str, TokenDef]:
    """Backward-compat shim if other code still calls this."""
    tokens, _ = _load_registry_for_version(version)
    return tokens
