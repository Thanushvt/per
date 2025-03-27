# app/migrations/0015_fix_roles_pk.py

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_alter_category_id_alter_education_id_alter_matter_id_and_more'),  # Or 0014 if applied
    ]

    operations = [
        # Fix Education state
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='education',
                    name='matter',
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='educations',
                        to='app.matter',
                        db_column='matterid'
                    ),
                ),
                migrations.AlterField(
                    model_name='education',
                    name='id',
                    field=models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    ),
                ),
            ],
            database_operations=[]
        ),
        # Fix Roles state
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='roles',
                    name='id',  # Remove default id if present
                ),
                migrations.AddField(
                    model_name='roles',
                    name='roleid',
                    field=models.AutoField(
                        primary_key=True,
                        serialize=False,
                        db_column='roleid'
                    ),
                ),
                migrations.AddField(
                    model_name='roles',
                    name='category',
                    field=models.ForeignKey(
                        blank=True,
                        db_column='category_id',
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='roles',
                        to='app.category'
                    ),
                ),
                migrations.AddField(
                    model_name='roles',
                    name='role',
                    field=models.TextField(
                        blank=True,
                        null=True,
                        db_column='rolename'
                    ),
                ),
            ],
            database_operations=[]
        ),
    ]