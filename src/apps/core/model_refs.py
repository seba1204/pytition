"""
Model reference constants to avoid circular imports.

Mainly used in ForeignKey and ManyToManyField definitions.
"""

PYTITION_USER = "accounts.PytitionUser"
ORGANIZATION = "organizations.Organization"
PETITION = "petitions.Petition"
PETITION_AUTHOR = "petitions.PetitionAuthor"
PETITION_RESOURCE = "petitions.PetitionResource"
PETITION_NEWS = "petitions.PetitionNews"
SIGNATURE = "signatures.Signature"
PETITION_TEMPLATE = "presets.PetitionTemplate"
SLUG_MODEL = "petitions.SlugModel"
PERMISSION = "accounts.Permission"
MODERATION_REASON = "moderation.ModerationReason"
MODERATION = "moderation.Moderation"
THEME = "theming.Theme"
