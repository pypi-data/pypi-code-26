# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-06-22 15:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial_after_reset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='catalog',
            field=models.ForeignKey(help_text='The catalog which will be used for this project.', on_delete=django.db.models.deletion.CASCADE, related_name='+', to='questions.Catalog', verbose_name='catalog'),
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.TextField(blank=True, help_text='You can use markdown syntax in the description.', verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='project',
            name='title',
            field=models.CharField(max_length=256, verbose_name='title'),
        ),
    ]
