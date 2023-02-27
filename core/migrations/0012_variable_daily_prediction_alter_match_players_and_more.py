# Generated by Django 4.1.2 on 2023-02-23 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_change_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='variable',
            name='daily_prediction',
            field=models.ManyToManyField(blank=True, null=True, to='core.match'),
        ),
        migrations.AlterField(
            model_name='match',
            name='players',
            field=models.ManyToManyField(blank=True, null=True, to='core.player'),
        ),
        migrations.AlterField(
            model_name='player',
            name='matches',
            field=models.ManyToManyField(blank=True, null=True, to='core.match'),
        ),
    ]