# Generated by Django 4.1.2 on 2023-02-25 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_variable_daily_prediction_alter_match_players_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='variable',
            name='enable_create_team',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='variable',
            name='enable_view_other_profile',
            field=models.BooleanField(default=False),
        ),
    ]
