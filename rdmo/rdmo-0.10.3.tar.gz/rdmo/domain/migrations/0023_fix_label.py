# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-07 13:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0022_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attributeentity',
            name='label',
            field=models.CharField(db_index=True, max_length=512),
        ),
    ]
