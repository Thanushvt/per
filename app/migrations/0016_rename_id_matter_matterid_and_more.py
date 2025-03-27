# app/migrations/0016_fix_matter_pk.py

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_rename_youtube_links_matter_youtube_and_more'),
    ]

    operations = [
        # Fix Matter state: set matterid as PK, adjust role
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='matter',
                    name='id',
                ),
                migrations.AddField(
                    model_name='matter',
                    name='matterid',
                    field=models.AutoField(
                        primary_key=True,
                        serialize=False,
                        db_column='matterid'
                    ),
                ),
                migrations.AlterField(
                    model_name='matter',
                    name='role',
                    field=models.ForeignKey(
                        blank=True,
                        db_column='role_id',  # Matches DB
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='matters',
                        to='app.roles'
                    ),
                ),
                migrations.RemoveField(
                    model_name='matter',
                    name='youtube_links',  # Remove from state if present
                ),
            ],
            database_operations=[]  # No schema changes
        ),
        # Remove unique_together from Category state if needed, no DB change
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterUniqueTogether(
                    name='category',
                    unique_together=set(),
                ),
            ],
            database_operations=[]  # Avoid index conflict
        ),
    ]