import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("petition", "0035_move_in_slugmodel"),
        ("petitions", "0002_move_in_petition"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name="signature",
                    name="petition",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="petitions.petition",
                    ),
                ),
            ],
        ),
    ]
