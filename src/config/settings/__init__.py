"""
Single entrypoint for Django settings.

Usage:
  export DJANGO_SETTINGS_MODULE="config.settings"

Behavior:
  - Load .env (highest precedence), then read OS env vars, then fall back to defaults.
  - Detect ENV ("dev" | "prod" | "test") in this order:
      1) .env: ENV or DEBUG
      2) OS env: ENV or DEBUG
      3) default -> "dev"
  - Apply per-env delta module (env/{dev/prod/test}.py).
  - Override ANY UPPERCASE setting from .env first, else from OS env.

Notes:
  - We intentionally keep this module dependency-free.
  - .env precedence over OS env is implemented by parsing .env into a local dict
    and consulting it BEFORE os.environ when overriding.
"""

from __future__ import annotations

from pathlib import Path

from .helpers.envtools import detect_env, load_dotenv, override_settings

# ──────────────────────────────────────────────────────────────────────────────
# .env loading (no external dependency)
# ──────────────────────────────────────────────────────────────────────────────

# Adjust this if your .env sits elsewhere:
PROJECT_ROOT = (
    Path(__file__).resolve().parents[3]
)  # src/config/settings/__init__.py -> src -> (repo root)
DOTENV_PATHS = [
    PROJECT_ROOT / ".env",
    PROJECT_ROOT / "src" / ".env",  # optional fallback
]

_DOTENV = load_dotenv(DOTENV_PATHS)
_ENV = detect_env(_DOTENV)


# ──────────────────────────────────────────────────────────────────────────────
# Load base modules (defaults)
# ──────────────────────────────────────────────────────────────────────────────

# First: core Django settings (safe defaults)
# Then: app/project defaults
from .default import *
from .django import *

# ──────────────────────────────────────────────────────────────────────────────
# Apply per-environment deltas
# ──────────────────────────────────────────────────────────────────────────────

if _ENV == "dev":
    from .delta.dev import *
elif _ENV == "prod":
    from .delta.prod import *
elif _ENV == "test":
    from .delta.test import *
else:
    # Should never happen, but keep dev-safe
    from .delta.dev import *

# Expose the resolved environment
SETTINGS_ENV = _ENV

# ──────────────────────────────────────────────────────────────────────────────
# Final overrides from env (.env first, then OS env)
# ──────────────────────────────────────────────────────────────────────────────

# Apply overrides
override_settings(globals(), _DOTENV)
