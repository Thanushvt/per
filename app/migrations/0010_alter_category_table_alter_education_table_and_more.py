# Generated by Django 5.1.5 on 2025-03-23 06:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_remove_job_youtube_links_matter_youtube_links'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='category',
            table='category',
        ),
        migrations.AlterModelTable(
            name='education',
            table='education',
        ),
        migrations.AlterModelTable(
            name='educationresource',
            table='educationresource',
        ),
        migrations.AlterModelTable(
            name='interest',
            table='interests',
        ),
        migrations.AlterModelTable(
            name='job',
            table='job',
        ),
        migrations.AlterModelTable(
            name='matter',
            table='matter',
        ),
        migrations.AlterModelTable(
            name='profile',
            table='profile',
        ),
        migrations.AlterModelTable(
            name='roles',
            table='roles',
        ),
        migrations.AlterModelTable(
            name='userselection',
            table='userselection',
        ),
    ]
