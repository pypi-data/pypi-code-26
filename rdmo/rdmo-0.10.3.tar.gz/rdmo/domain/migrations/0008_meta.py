# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-07-18 10:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0007_db_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attributeentity',
            name='parent_collection',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='domain.AttributeEntity'),
        ),
    ]
