from django.db import migrations


def move_ct(apps, schema_editor):
    # Update django_content_type
    # from app_label 'petition' to 'accounts' for model 'pytitionuser'
    # Then auth_permission follows via FK to content_type_id
    with schema_editor.connection.cursor() as cur:
        cur.execute("""
            UPDATE django_content_type
               SET app_label = 'accounts'
             WHERE app_label = 'petition' AND model = 'pytitionuser';
        """)


def reverse_move_ct(apps, schema_editor):
    with schema_editor.connection.cursor() as cur:
        cur.execute("""
            UPDATE django_content_type
               SET app_label = 'petition'
             WHERE app_label = 'accounts' AND model = 'pytitionuser';
        """)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_state_only"),
    ]
    operations = [
        migrations.RunPython(move_ct, reverse_move_ct),
    ]
