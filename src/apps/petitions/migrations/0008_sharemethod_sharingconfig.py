"""Migration to create ShareMethod and SharingConfig models."""

from typing import Any

import django.db.models.deletion
from django.db import migrations, models


def create_default_share_methods(apps: Any, schema_editor: Any) -> None:
    """Create default share methods with sensible default metadata."""
    ShareMethod = apps.get_model("petitions", "ShareMethod")

    defaults = [
        {
            "code": "facebook",
            "label": "Facebook",
            "is_builtin": True,
            "default_position": 1,
            "default_data": {
                "share_url": "https://www.facebook.com/sharer/sharer.php?u={url}"
            },
            "schema": {"url": "string"},
            "icon": "bi-facebook",
        },
        {
            "code": "x",
            "label": "X (Twitter)",
            "is_builtin": True,
            "default_position": 2,
            "default_data": {
                "share_url": "https://twitter.com/intent/tweet?url={url}&text={text}"
            },
            "schema": {"url": "string", "text": "string"},
            "icon": "bi-twitter-x",
        },
        {
            "code": "email",
            "label": "Email",
            "is_builtin": True,
            "default_position": 3,
            "default_data": {"share_url": "mailto:?subject={subject}&body={body}"},
            "schema": {"subject": "string", "body": "string"},
            "icon": "bi-envelope-fill",
        },
        {
            "code": "mastodon",
            "label": "Mastodon",
            "is_builtin": True,
            "default_position": 4,
            "default_data": {
                "share_url": "https://mastodon.social/share?text={text}%20{url}"
            },
            "schema": {"url": "string", "text": "string"},
            "icon": "bi-mastodon",
        },
        {
            "code": "bluesky",
            "label": "Bluesky",
            "is_builtin": True,
            "default_position": 5,
            "default_data": {
                "share_url": "https://bsky.app/intent/compose?text={text}%20{url}"
            },
            "schema": {"url": "string", "text": "string"},
            "icon": "bi-cloud-fill",
        },
        {
            "code": "qrcode",
            "label": "QR Code",
            "is_builtin": True,
            "default_position": 6,
            "default_data": {"generator": "internal"},
            "schema": {"url": "string"},
            "icon": "bi-qr-code",
        },
    ]

    for entry in defaults:
        ShareMethod.objects.create(**entry)


def delete_default_share_methods(apps: Any, schema_editor: Any) -> None:
    """Rollback default share methods."""
    ShareMethod = apps.get_model("core", "ShareMethod")
    ShareMethod.objects.filter(is_builtin=True).delete()


class Migration(migrations.Migration):
    """Migration to create ShareMethod and SharingConfig models."""

    dependencies = [
        ("core", "0001_initial"),
        ("petitions", "0007_doublingthreshold_fixedpercentthreshold_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShareMethod",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code", models.SlugField(unique=True)),
                ("label", models.CharField(max_length=100)),
                ("is_builtin", models.BooleanField(default=True)),
                ("default_position", models.PositiveIntegerField(default=0)),
                ("default_data", models.JSONField(blank=True, default=dict)),
                ("schema", models.JSONField(blank=True, default=dict)),
                ("icon", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "ordering": ["default_position", "code"],
            },
        ),
        migrations.RunPython(
            create_default_share_methods,
            delete_default_share_methods,
        ),
        migrations.CreateModel(
            name="SharingConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="A human-readable name for this sub-configuration.",
                        max_length=255,
                        verbose_name="Name",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Timestamp when this sub-config was created.",
                        verbose_name="Created at",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Timestamp when this sub-config was last updated.",
                        verbose_name="Updated at",
                    ),
                ),
                (
                    "bundle",
                    models.OneToOneField(
                        help_text=(
                            "The configuration bundle this sub-config belongs to."
                        ),
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_item",
                        to="core.configbundle",
                        verbose_name="Configuration bundle",
                    ),
                ),
                (
                    "methods",
                    models.ManyToManyField(
                        blank=True,
                        related_name="sharing_configs",
                        to="petitions.sharemethod",
                    ),
                ),
            ],
            options={
                "verbose_name": "Sharing configuration",
            },
        ),
    ]
