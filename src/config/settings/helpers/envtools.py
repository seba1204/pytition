"""
envtools.py — Small helpers for .env loading, environment detection, and overrides.

Design goals:
- No external dependencies
- Clear precedence: .env > OS env > Python defaults
- Side-effect free: pure functions that the settings entrypoint calls explicitly
"""

from __future__ import annotations
import os
import ast
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional


def load_dotenv(paths: Iterable[Path]) -> Dict[str, str]:
    """
    Parse .env files in order and return a flat dict of key -> value.
    Later files in `paths` override earlier ones (last-wins).
    Supports simple lines:
      KEY=value
      KEY="value with spaces"
    Ignores comments (#...) and blank lines.
    """
    envmap: Dict[str, str] = {}
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    envmap[k] = v
        except FileNotFoundError:
            continue
    return envmap


def get_env(name: str, dotenv: Mapping[str, str], osenv: Mapping[str, str] | None = None) -> Optional[str]:
    """
    Return a value for `name` with precedence:
      1) `dotenv` map
      2) `osenv` (defaults to os.environ)
    """
    if name in dotenv:
        return dotenv[name]
    if osenv is None:
        osenv = os.environ
    return osenv.get(name)


def to_bool(value: str) -> bool:
    """Best-effort boolean coercion for common truthy strings."""
    return value.lower() in {"1", "true", "yes", "on"}


def detect_env(dotenv: Mapping[str, str], osenv: Mapping[str, str] | None = None, default: str = "dev") -> str:
    """
    Decide between "dev" | "prod" | "test".
    Priority: ENV (in .env then OS) -> DEBUG (in .env then OS) -> default.
    If DEBUG is truthy => "dev", else => "prod".
    """
    env = get_env("ENV", dotenv, osenv)
    if env:
        env = env.strip().lower()
        if env in {"dev", "prod", "test"}:
            return env

    dbg = get_env("DEBUG", dotenv, osenv)
    if dbg is not None:
        return "dev" if to_bool(dbg) else "prod"

    return default


def coerce_like(original: Any, newval: str) -> Any:
    """
    Try to coerce string `newval` to the type/shape of `original`.
    - bool: common truthy/falsey strings
    - ast.literal_eval for safe Python literals (int/float/list/dict/tuple/None/bool)
    - if original is list/tuple: accept comma-separated strings as list
    - fallback: raw string
    """
    if isinstance(original, bool):
        return to_bool(newval)
    try:
        return ast.literal_eval(newval)
    except Exception:
        pass
    if isinstance(original, (list, tuple)):
        return [x.strip() for x in newval.split(",") if x.strip()]
    return newval


def override_settings(globals_dict: Dict[str, Any], dotenv: Mapping[str, str], osenv: Mapping[str, str] | None = None) -> None:
    """
    For every UPPERCASE key in `globals_dict`, override its value using:
      1) .env (dotenv)
      2) OS env (osenv, default os.environ)
    Uses `coerce_like` to cast strings to appropriate types.
    """
    if osenv is None:
        osenv = os.environ

    for key, current in list(globals_dict.items()):
        if not key.isupper():
            continue
        env_val = get_env(key, dotenv, osenv)
        if env_val is None:
            continue
        globals_dict[key] = coerce_like(current, env_val)
