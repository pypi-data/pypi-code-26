# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-10 08:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('edxval', '0006_auto_20171009_0725'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThirdPartyTranscriptCredentialsState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('org', models.CharField(max_length=32, verbose_name=b'Course Organization')),
                ('provider', models.CharField(choices=[(b'Custom', b'Custom'), (b'3PlayMedia', b'3PlayMedia'), (b'Cielo24', b'Cielo24')], max_length=20, verbose_name=b'Transcript Provider')),
                ('exists', models.BooleanField(default=False, help_text=b'Transcript credentials state')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='thirdpartytranscriptcredentialsstate',
            unique_together=set([('org', 'provider')]),
        ),
    ]
