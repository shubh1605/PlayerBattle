# Generated by Django 4.1.2 on 2023-02-17 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_change'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='date',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='team_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
