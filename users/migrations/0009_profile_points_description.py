# Generated by Django 4.1.2 on 2023-02-18 09:35

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_profile_bonus_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='points_description',
            field=jsonfield.fields.JSONField(blank=True, default=dict, null=True),
        ),
    ]