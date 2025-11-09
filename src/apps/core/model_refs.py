"""
Model reference constants to avoid circular imports.

Mainly used in ForeignKey and ManyToManyField definitions.
"""

# --- Core models -----------------------------------------------------------
CONFIG_BUNDLE = "core.ConfigBundle"
BASE_SUB_CONFIG = "core.BaseSubConfig"
HAS_CONFIG = "core.HasConfig"
HAS_OWNER = "core.HasOwner"

PYTITION_USER = "accounts.PytitionUser"
ORGANIZATION = "organizations.Organization"

# --- Consents models ------------------------------------------------------
CONSENT = "consents.Consent"
OPT_IN_CONFIG = "consents.OptInConfig"

# --- Petition models -------------------------------------------------------
PETITION = "petitions.Petition"
PETITION_AUTHOR = "petitions.PetitionAuthor"
PETITION_RESOURCE = "petitions.PetitionResource"
PETITION_NEWS = "petitions.PetitionNews"

SHARING_CONFIG = "petitions.SharingConfig"
THRESHOLD_CONFIG = "petitions.ThresholdConfig"

# --- Signature models ------------------------------------------------------
SIGNATURE = "signatures.Signature"
PETITION_TEMPLATE = "presets.PetitionTemplate"
SLUG_MODEL = "petitions.SlugModel"
PERMISSION = "accounts.Permission"
MODERATION_REASON = "moderation.ModerationReason"
MODERATION = "moderation.Moderation"
THEME = "theming.Theme"

# --- Notification models ---------------------------------------------------
SMTP_CONFIG = "notifications.config.SMTPConfig"
MAIL_TEMPLATE_CONFIG = "notifications.config.MailConfig"
WEBHOOK_CONFIG = "notifications.config.WebhookConfig"


def split_label(label: str) -> tuple[str, str]:
    """
    Split 'app_label.ModelName' into a (app_label, model) tuple (lowercased).

    Parameters
    ----------
    label : str
        Dotted label, e.g. "accounts.PytitionUser".

    Returns
    -------
    tuple of (str, str)
        (app_label_lower, model_lower)
    """
    app_label, model = label.split(".", 1)
    return app_label.lower(), model.lower()
