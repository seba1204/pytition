"""Migration to merge `twitter_image`into `illustration` from the Petition model."""

from __future__ import annotations

from django.db import migrations


def forwards(apps, schema_editor) -> None:
    """Move twitter_image path into illustration, then drop twitter_image.

    Notes
    -----
    - We do not read the file content; we directly set the ImageField's *name*,
      which is the path relative to the storage (MEDIA_ROOT). This is sufficient
      for Django to point to the existing file on disk/storage.
    - If both `illustration` and `twitter_image` were set, `twitter_image` wins.
    """
    Petition = apps.get_model("petitions", "Petition")

    for p in Petition.objects.exclude(twitter_image="").iterator():
        tw_path = getattr(p, "twitter_image", "") or ""
        if not tw_path:
            continue
        try:
            # if tw_path starts with MEDIA_ROOT, remove it to make it
            # relative to storage
            if tw_path.startswith("/media/"):
                tw_path = tw_path[len("/media/") :]
            print(f"Setting illustration for Petition id={p.id} to '{tw_path}'")
            p.illustration.name = tw_path
            p.save(update_fields=["illustration"])
        except Exception:
            continue


def backwards(apps, schema_editor) -> None:
    """Recreate `twitter_image` from `illustration` when reversing.

    Notes
    -----
    - We attempt to restore `twitter_image` from `illustration.name`.
    - If `illustration` is empty, we leave `twitter_image` empty.
    """
    Petition = apps.get_model("petitions", "Petition")

    for p in Petition.objects.all().iterator():
        ill = getattr(p, "illustration", None)
        ill_name = getattr(ill, "name", "") or ""
        try:
            p.twitter_image = ill_name
            p.save(update_fields=["twitter_image"])
        except Exception:
            continue


class Migration(migrations.Migration):
    """Migration to merge `twitter_image`into `illustration` from the Petition model."""

    dependencies = [
        ("petitions", "0005_petitionnews_petitionresource_petitionauthor"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
        migrations.RemoveField(
            model_name="petition",
            name="twitter_image",
        ),
    ]
