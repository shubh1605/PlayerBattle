# Generated by Django 4.1.2 on 2023-02-23 05:42

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_profile_daily_prediction'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='daily_prediction2',
            field=jsonfield.fields.JSONField(blank=True, default='{}', null=True),
        ),
    ]
