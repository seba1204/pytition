from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="PytitionUser",
                    fields=[
                        ("id", models.BigAutoField(primary_key=True, serialize=False)),
                        ("moderated", models.BooleanField(default=False)),
                        # We do not create DB constraints here;
                        # FKs are state-only initially
                        (
                            "user",
                            models.OneToOneField(
                                on_delete=models.deletion.CASCADE,
                                related_name="pytitionuser",
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                    ],
                    options={
                        "db_table": "petition_pytitionuser",
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
