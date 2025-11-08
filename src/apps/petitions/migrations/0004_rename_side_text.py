"""Migration to rename Petition.side_text to Petition.tagline."""
from __future__ import annotations

from django.db import migrations


class Migration(migrations.Migration):
    """Migration to rename Petition.side_text to Petition.tagline."""

    dependencies = [
        ("petitions", "0003_petition_illustration"),
    ]

    operations = [
        migrations.RenameField(
            model_name="petition",
            old_name="side_text",
            new_name="tagline",
        ),
    ]
