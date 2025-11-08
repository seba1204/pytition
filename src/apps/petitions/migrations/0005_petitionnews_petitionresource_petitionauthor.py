"""Migration script to create PetitionNews, PetitionResource, PetitionAuthor models."""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Migration to create PetitionNews, PetitionResource, PetitionAuthor models."""

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("petitions", "0004_rename_side_text"),
    ]

    operations = [
        migrations.CreateModel(
            name="PetitionNews",
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
                ("title", models.CharField(max_length=255)),
                ("content", models.TextField(blank=True)),
                ("date", models.DateField()),
                (
                    "petition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="news",
                        to="petitions.petition",
                    ),
                ),
            ],
            options={
                "ordering": ["-date", "-id"],
            },
        ),
        migrations.CreateModel(
            name="PetitionResource",
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
                ("title", models.CharField(blank=True, max_length=255)),
                ("file", models.FileField(upload_to="petition_resources/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "petition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="resources",
                        to="petitions.petition",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PetitionAuthor",
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
                ("object_id", models.PositiveIntegerField()),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "petition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="authorship",
                        to="petitions.petition",
                    ),
                ),
            ],
            options={
                "unique_together": {("petition", "content_type", "object_id")},
            },
        ),
    ]
