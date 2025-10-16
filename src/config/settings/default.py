"""
Project/application defaults.
Keep it lean. Everything remains overrideable via .env / ENV.
"""

from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────────
# Site / Branding
# ──────────────────────────────────────────────────────────────────────────────

SITE_NAME = "Pytition"

# ──────────────────────────────────────────────────────────────────────────────
# Pagination / UI
# ──────────────────────────────────────────────────────────────────────────────

PAGINATOR_COUNT = 20

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
UWSGI_WAIT_FOR_MAIL_SEND_IN_S = 5 # wait before sending mails
UWSGI_WAIT_FOR_RETRY_IN_S = 60 # 1 min between retries
UWSGI_WAIT_FOR_PURGE_IN_S = 86400 # 1 day between purges
UWSGI_NB_DAYS_TO_KEEP = 7 # keep sent/failed mails for 7 days

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

TINYMCE_DEFAULT_CONFIG = {
    "plugins": "print preview fullpage searchreplace autolink directionality visualblocks visualchars fullscreen image link media template codesample table charmap hr pagebreak nonbreaking anchor toc insertdatetime advlist lists textcolor wordcount imagetools contextmenu colorpicker textpattern help",
    "cleanup_on_startup": True,
    "custom_undo_redo_levels": 10,
    "toolbar1": "formatselect | bold italic strikethrough forecolor backcolor | link | alignleft aligncenter alignright alignjustify  | numlist bullist outdent indent  | removeformat | fontselect | fontsizeselect",
    "insert_toolbar": "forecolor backcolor",
    "fontsize_formats": "8pt 10pt 12pt 14pt 18pt 24pt 36pt",
    "entity_encoding": "raw",
    "relative_urls" : False,
    "convert_urls": True,
    "file_picker_types": "image",
    "automatic_uploads": True,
    "images_upload_url": "/petition/image_upload",
    "image_upload_credentials": True,
    "images_upload_handler": """function(blobInfo, success, failure) {
        let xhr = new XMLHttpRequest();
        xhr.open("POST", get_image_upload_url());
        xhr.setRequestHeader("X-CSRFTOKEN", get_csrf_token()); // manually set header

        xhr.onload = function() {
            if (xhr.status !== 200) {
                failure("HTTP Error: " + xhr.status);
                return;
            }

            let json = JSON.parse(xhr.responseText);

            if (!json || typeof json.location !== "string") {
                failure("Invalid JSON: " + xhr.responseText);
                return;
            }

            success(json.location);
        };

        let formData = new FormData();
        formData.append("file", blobInfo.blob(), blobInfo.filename());

        xhr.send(formData);
        }
    """,
    "setup": """function(ed) {
       ed.on("change", function(e) {
            set_mce_changed(ed);
       });}""",
}
TINYMCE_INCLUDE_JQUERY = True

# ──────────────────────────────────────────────────────────────────────────────
# Homepage
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_INDEX_THUMBNAIL = "/img/petition_icon.svg"
FOOTER_TEMPLATE = None
INDEX_PAGE = "HOME"   # "ORGA_PROFILE" / "USER_PROFILE" / "LOGIN_REGISTER"

# ──────────────────────────────────────────────────────────────────────────────
# Anti-bot
# ──────────────────────────────────────────────────────────────────────────────

SIGNATURE_THROTTLE = 5                 # allowed signatures from same IP
SIGNATURE_THROTTLE_TIMING = 60*60*24   # time window in seconds (1 day)