# Generated by Django 4.1.2 on 2023-01-28 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_profile_captain_changes_profile_vice_captain_changes'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='rank',
            field=models.PositiveIntegerField(blank=True, default=1, null=True),
        ),
    ]
