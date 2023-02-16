# Generated by Django 4.1.2 on 2022-11-05 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_variable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='matches',
        ),
        migrations.AddField(
            model_name='player',
            name='matches',
            field=models.ManyToManyField(to='core.match'),
        ),
    ]
