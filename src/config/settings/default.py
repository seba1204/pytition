"""
Project/application defaults.

Keep it lean. Everything remains overrideable via .env / ENV.
"""

from __future__ import annotations

from typing import Any

# ──────────────────────────────────────────────────────────────────────────────
# Site / Branding
# ──────────────────────────────────────────────────────────────────────────────

SITE_NAME = "Pytition"

# ──────────────────────────────────────────────────────────────────────────────
# Pagination / UI
# ──────────────────────────────────────────────────────────────────────────────

PAGINATOR_COUNT = 12  # items per page

# ──────────────────────────────────────────────────────────────────────────────
# Feature flags (examples)
# ──────────────────────────────────────────────────────────────────────────────

ALLOW_REGISTER = True
DISABLE_USER_PETITION = False
RESTRICT_ORG_CREATION = False

# ──────────────────────────────────────────────────────────────────────────────
# Email defaults (examples)
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_NOREPLY_MAIL = "noreply@domain.tld"
USE_MAIL_QUEUE = False
MAIL_EXTERNAL_CRON_SET = False

# If you run under uWSGI and have mail queue workers
UWSGI_WAIT_FOR_MAIL_SEND_IN_S = 5  # wait before sending mails
UWSGI_WAIT_FOR_RETRY_IN_S = 60  # 1 min between retries
UWSGI_WAIT_FOR_PURGE_IN_S = 86400  # 1 day between purges
UWSGI_NB_DAYS_TO_KEEP = 7  # keep sent/failed mails for 7 days

# ──────────────────────────────────────────────────────────────────────────────
# Maintenance mode (example placeholders)
# ──────────────────────────────────────────────────────────────────────────────

MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
MAINTENANCE_MODE_STATE_FILE_PATH = "/tmp/pytition_maintenance_mode"

# ──────────────────────────────────────────────────────────────────────────────
# Language setup extras
# ──────────────────────────────────────────────────────────────────────────────
PHONENUMBER_DEFAULT_REGION = "FR"
# ──────────────────────────────────────────────────────────────────────────────
# UI / Editor
# ──────────────────────────────────────────────────────────────────────────────

TINYMCE_DEFAULT_CONFIG: dict[str, Any] = {
    "license_key": "gpl",
    "height": 400,
    "menubar": False,
    "plugins": "lists link image table",
    "toolbar": (
        "undo redo | styles | bold italic underline | "
        "alignleft aligncenter alignright | bullist numlist | "
        "link image | table"
    ),
    "promotion": False,
    "branding": False,
    "block_formats": "Paragraph=p; Heading 2=h2; Heading 3=h3; Heading 4=h4",
}

# ──────────────────────────────────────────────────────────────────────────────
# Homepage
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_INDEX_THUMBNAIL = "/img/logo_placeholder.svg"

FOOTER_TEMPLATE: str | None = None
INDEX_PAGE = "HOME"  # "ORGA_PROFILE" / "USER_PROFILE" / "LOGIN_REGISTER"

# ──────────────────────────────────────────────────────────────────────────────
# Anti-bot
# ──────────────────────────────────────────────────────────────────────────────

SIGNATURE_THROTTLE = 5  # allowed signatures from same IP
SIGNATURE_THROTTLE_TIMING = 60 * 60 * 24  # time window in seconds (1 day)

# ──────────────────────────────────────────────────────────────────────────────
# Assets / PWA
# ──────────────────────────────────────────────────────────────────────────────
ASSETS_IMAGE_SIZES = {
    "thumbnail": 200,  # max width
    "standard": 800,
    "retina": 1600,
}
ASSETS_IMAGE_QUALITY = 85  # WebP quality
ASSETS_FAVICON_SIZES = [16, 32, 48]
ASSETS_APPLE_TOUCH_SIZE = 180
ASSETS_ANDROID_ICON_SIZES = [192, 512]
ASSETS_PWA_NAME = SITE_NAME
ASSETS_PWA_SHORT_NAME = SITE_NAME
ASSETS_PWA_THEME_COLOR = "#0d6efd"
ASSETS_PWA_BG_COLOR = "#ffffff"
ASSETS_PWA_START_URL = "/"
ASSETS_PWA_DISPLAY = "standalone"


# ──────────────────────────────────────────────────────────────────────────────
# Documentation i18n setup
# ──────────────────────────────────────────────────────────────────────────────

SPHINX_LANGUAGE = "en"


# ──────────────────────────────────────────────────────────────────────────────
# Theming / CSS Token Registry
# ──────────────────────────────────────────────────────────────────────────────

THEME_TOKEN_REGISTRY = {
    "v1": "src/apps/theming/registry/tokens_v1.json",
}

THEME_ALLOWED_TOKEN_SCOPES: set[str] = {
    ":root",
    '[data-bs-theme="dark"]',
}
