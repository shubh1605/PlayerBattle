# Generated by Django 4.1.2 on 2023-04-06 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_notification_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='chosen_team',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]