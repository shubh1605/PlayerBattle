# Generated by Django 4.1.2 on 2022-12-30 10:03

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_profile_contact_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='points',
            field=jsonfield.fields.JSONField(blank=True, default=dict, null=True),
        ),
    ]
