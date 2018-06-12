# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import pwdprotect.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordProtectedUrl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(unique=True, max_length=255, verbose_name='URL', validators=[pwdprotect.models.LocalUrlValidator()])),
                ('username', models.CharField(max_length=50, verbose_name='Username')),
                ('password', models.CharField(default=pwdprotect.models.make_password, max_length=50, verbose_name='Password')),
            ],
            options={
                'verbose_name': 'protected URL',
                'verbose_name_plural': 'protected URLs',
            },
        ),
    ]
