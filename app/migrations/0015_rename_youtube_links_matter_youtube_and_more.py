# app/migrations/0015_fix_matter_and_roles.py

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_alter_category_unique_together_and_more'),
    ]

    operations = [
        # Ensure Matter state matches database (youtube, not youtube_links)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='matter',
                    name='youtube',
                    field=models.TextField(null=True, blank=True),  # Use TextField, adjust if longtext needed
                ),
                migrations.AddField(
                    model_name='matter',
                    name='role',
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='matters',
                        to='app.roles',
                        db_column='role_id',
                        null=True,
                        blank=True
                    ),
                ),
            ],
            database_operations=[]  # No schema change needed
        ),
        # Fix Roles state to ensure roleid is PK
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(  # Use AlterField if id was present, else skip
                    model_name='roles',
                    name='roleid',
                    field=models.AutoField(
                        primary_key=True,
                        serialize=False,
                        db_column='roleid'
                    ),
                ),
            ],
            database_operations=[]
        ),
    ]