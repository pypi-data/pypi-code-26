# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-05-26 13:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matialvarezs_grafana_customers', '0006_auto_20180525_1217'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboardgrafana',
            name='title',
            field=models.CharField(default='', max_length=100),
        ),
    ]
