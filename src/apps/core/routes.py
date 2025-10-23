"""
Lightweight helpers for string-based, namespaced route enums.

This module intentionally avoids custom meta classes or enum bases.
Each app declares a plain `StrEnum` whose members are fully-qualified route
names (e.g., "organizations:add_user"). These members are strings, so they can
be passed directly to :func:`django.urls.reverse` and the `{% url %}` tag.

This module provides:
- :class:`Route` dataclass (pattern + view callable),
- :func:`short_name` to extract the short part of a fully-qualified name,
- :func:`build_urlpatterns` to construct short-named `urlpatterns`,
- :func:`validate_bijection` to ensure mapping coverage (fail-fast on import).

Examples
--------
>>> short_name("organizations:add_user")
'add_user'
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import TypeVar

from django.http import HttpResponse
from django.urls import URLPattern, path

# --------------------------------------------------------------------------- #
# Types
# --------------------------------------------------------------------------- #

DjangoView = Callable[..., HttpResponse]
E = TypeVar("E", bound=StrEnum)


# --------------------------------------------------------------------------- #
# Data structures
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Route:
    """
    Bind a URL path pattern to a Django view.

    Parameters
    ----------
    pattern : str
        URL pattern (e.g., "create/" or "<slug:org_slug>/").
    view : DjangoView
        A function- or class-based view callable that Django can dispatch.
    """

    pattern: str
    view: DjangoView


# --------------------------------------------------------------------------- #
# Utilities
# --------------------------------------------------------------------------- #


SPLIT_PARTS_COUNT = 2


def short_name(full: str) -> str:
    """
    Extract the short route name from a fully-qualified name.

    Parameters
    ----------
    full : str
        Fully-qualified name of the form "<namespace>:<short>" or "<short>".

    Returns
    -------
    str
        The short part (text after the first colon),
        or the input string if no colon is present.

    Examples
    --------
    >>> short_name("organizations:add_user")
    'add_user'
    >>> short_name("dashboard")
    'dashboard'
    """
    parts = full.split(":", 1)
    return parts[1] if len(parts) == SPLIT_PARTS_COUNT else full


def build_urlpatterns(mapping: Mapping[E, Route]) -> list[URLPattern]:
    """
    Build Django `urlpatterns` from a mapping of enum members to routes.

    Notes
    -----
    The name assigned to each pattern is the *short* part of the enum value,
    i.e., everything after the first colon. The project router must supply the
    Django namespace via ``include(..., namespace="...")``.

    Parameters
    ----------
    mapping : Mapping[E, Route]
        One-to-one mapping from enum members (fully-qualified names) to `Route`.

    Returns
    -------
    list of django.urls.URLPattern
        URL patterns with short names.
    """
    patterns: list[URLPattern] = []
    for member, route in mapping.items():
        name = short_name(str(member))
        patterns.append(path(route.pattern, route.view, name=name))
    return patterns


def validate_bijection(enum_cls: type[E], mapping: Mapping[E, Route]) -> None:
    """
    Validate that `mapping` covers exactly all members of `enum_cls`.

    Use this early (at import time) to fail fast during CI/startup.

    Parameters
    ----------
    enum_cls : type[E]
        The `StrEnum` subclass that declares the route names.
    mapping : Mapping[E, Route]
        Mapping from enum members to route definitions.

    Raises
    ------
    AssertionError
        If the mapping is missing members or contains extra keys.
    """
    enum_members: list[E] = list(enum_cls)
    enum_set = set(enum_members)
    map_set = set(mapping.keys())

    missing = enum_set.difference(map_set)
    extra = map_set.difference(enum_set)

    if missing:
        missing_list = ", ".join(sorted(m.name for m in missing))
        raise AssertionError(f"[{enum_cls.__name__}] Missing routes: {missing_list}")
    if extra:
        extra_list = ", ".join(sorted(m.name for m in extra))
        raise AssertionError(f"[{enum_cls.__name__}] Extra routes: {extra_list}")
