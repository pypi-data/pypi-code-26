# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-28 11:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_data_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='value',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='projects.Project'),
        ),
    ]
