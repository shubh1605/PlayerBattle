# Generated by Django 4.1.2 on 2023-02-23 05:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_profile_daily_prediction2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='daily_prediction2',
        ),
    ]
