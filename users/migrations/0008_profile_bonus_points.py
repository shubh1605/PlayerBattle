# Generated by Django 4.1.2 on 2023-02-18 05:50

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_profile_orange_cap_profile_purple_cap'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='bonus_points',
            field=jsonfield.fields.JSONField(blank=True, default=dict, null=True),
        ),
    ]