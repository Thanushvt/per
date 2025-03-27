# app/migrations/0017_fix_interest_and_matter.py

import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('app', '0016_rename_id_matter_matterid_and_more'),
    ]
    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='interest',
                    name='id',  # Remove implicit id
                ),
                migrations.AddField(
                    model_name='interest',
                    name='interestid',
                    field=models.AutoField(
                        primary_key=True,
                        serialize=False,
                        db_column='interestid'
                    ),
                ),
                migrations.AlterField(
                    model_name='matter',
                    name='role',
                    field=models.ForeignKey(
                        blank=True,
                        db_column='role_id',
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='matters',
                        to='app.roles'
                    ),
                ),
            ],
            database_operations=[]  # No schema change
        ),
    ]