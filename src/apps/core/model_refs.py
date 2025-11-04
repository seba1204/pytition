"""
Model reference constants to avoid circular imports.

Mainly used in ForeignKey and ManyToManyField definitions.
"""

PYTITION_USER = "accounts.PytitionUser"
ORGANIZATION = "organizations.Organization"
PETITION = "petitions.Petition"
SIGNATURE = "signatures.Signature"
PETITION_TEMPLATE = "presets.PetitionTemplate"
SLUG_MODEL = "petitions.SlugModel"
PERMISSION = "accounts.Permission"
MODERATION_REASON = "moderation.ModerationReason"
MODERATION = "moderation.Moderation"
