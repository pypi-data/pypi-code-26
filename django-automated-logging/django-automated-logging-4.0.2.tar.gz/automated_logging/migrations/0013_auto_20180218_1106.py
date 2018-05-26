# Generated by Django 2.0.2 on 2018-02-18 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automated_logging', '0012_auto_20180218_1101'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='request',
            name='url',
        ),
        migrations.AddField(
            model_name='request',
            name='uri',
            field=models.URLField(default='/'),
            preserve_default=False,
        ),
    ]
