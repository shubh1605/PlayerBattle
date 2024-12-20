# Generated by Django 4.1.2 on 2022-11-04 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='has_completed',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='match',
            name='is_live',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
