# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-21 20:44
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.CharField(max_length=255, unique=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=50)),
                ('object_type', models.CharField(max_length=50)),
                ('object_id', models.PositiveIntegerField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('revision_id', models.PositiveIntegerField(db_index=True, default=0)),
                ('head', models.BooleanField(db_index=True, default=False)),
                ('is_published', models.BooleanField(db_index=True, default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('published_version', models.PositiveIntegerField(null=True)),
                ('latest_version', models.PositiveIntegerField(null=True)),
                ('slug', models.SlugField(max_length=255)),
                ('shares', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('views', models.PositiveIntegerField(default=0)),
                ('template', models.CharField(default=b'default', max_length=255)),
                ('template_data', jsonfield.fields.JSONField(default={})),
                ('seo_keyword', models.CharField(max_length=100, null=True)),
                ('seo_description', models.TextField(null=True)),
                ('integrations', jsonfield.fields.JSONField(default={})),
                ('content', jsonfield.fields.JSONField(default=[])),
                ('snippet', models.TextField(null=True)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('published_at', models.DateTimeField(null=True)),
                ('headline', models.CharField(max_length=255)),
                ('importance', models.PositiveIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=3, validators=[django.core.validators.MaxValueValidator(5)])),
                ('reading_time', models.CharField(choices=[(b'anytime', b'Anytime'), (b'morning', b'Morning'), (b'midday', b'Midday'), (b'evening', b'Evening')], default=b'anytime', max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('article', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dispatch.Article')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to=b'files/%Y/%m')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(upload_to=b'images/%Y/%m')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('width', models.PositiveIntegerField(blank=True, null=True)),
                ('height', models.PositiveIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ImageAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.TextField(blank=True, null=True)),
                ('credit', models.TextField(blank=True, null=True)),
                ('order', models.PositiveIntegerField(null=True)),
                ('article', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='article', to='dispatch.Article')),
            ],
        ),
        migrations.CreateModel(
            name='ImageGallery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('images', models.ManyToManyField(related_name='images', to='dispatch.ImageAttachment')),
            ],
        ),
        migrations.CreateModel(
            name='Integration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('integration_id', models.CharField(max_length=100, unique=True)),
                ('settings', models.TextField(default=b'{}')),
            ],
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('revision_id', models.PositiveIntegerField(db_index=True, default=0)),
                ('head', models.BooleanField(db_index=True, default=False)),
                ('is_published', models.BooleanField(db_index=True, default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('published_version', models.PositiveIntegerField(null=True)),
                ('latest_version', models.PositiveIntegerField(null=True)),
                ('slug', models.SlugField(max_length=255)),
                ('shares', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('views', models.PositiveIntegerField(default=0)),
                ('template', models.CharField(default=b'default', max_length=255)),
                ('template_data', jsonfield.fields.JSONField(default={})),
                ('seo_keyword', models.CharField(max_length=100, null=True)),
                ('seo_description', models.TextField(null=True)),
                ('integrations', jsonfield.fields.JSONField(default={})),
                ('content', jsonfield.fields.JSONField(default=[])),
                ('snippet', models.TextField(null=True)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('published_at', models.DateTimeField(null=True)),
                ('title', models.CharField(max_length=255)),
                ('featured_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='page_featured_image', to='dispatch.ImageAttachment')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='page_parent', to='dispatch.Page')),
                ('parent_page', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent_page_fk', to='dispatch.Page')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=255, null=True)),
                ('is_admin', models.BooleanField(default=True)),
                ('image', models.ImageField(null=True, upload_to=b'images')),
                ('slug', models.SlugField(null=True, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('last_used', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('zone_id', models.SlugField(primary_key=True, serialize=False)),
                ('widget_id', models.SlugField(null=True)),
                ('data', jsonfield.fields.JSONField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='imageattachment',
            name='gallery',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dispatch.ImageGallery'),
        ),
        migrations.AddField(
            model_name='imageattachment',
            name='image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='image', to='dispatch.Image'),
        ),
        migrations.AddField(
            model_name='imageattachment',
            name='page',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='page', to='dispatch.Page'),
        ),
        migrations.AddField(
            model_name='image',
            name='authors',
            field=models.ManyToManyField(related_name='authors', through='dispatch.Author', to='dispatch.Person'),
        ),
        migrations.AddField(
            model_name='author',
            name='image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dispatch.Image'),
        ),
        migrations.AddField(
            model_name='author',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dispatch.Person'),
        ),
        migrations.AddField(
            model_name='article',
            name='authors',
            field=models.ManyToManyField(related_name='authors_set', through='dispatch.Author', to='dispatch.Person'),
        ),
        migrations.AddField(
            model_name='article',
            name='featured_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='article_featured_image', to='dispatch.ImageAttachment'),
        ),
        migrations.AddField(
            model_name='article',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='article_parent', to='dispatch.Article'),
        ),
        migrations.AddField(
            model_name='article',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dispatch.Section'),
        ),
        migrations.AddField(
            model_name='article',
            name='tags',
            field=models.ManyToManyField(to='dispatch.Tag'),
        ),
        migrations.AddField(
            model_name='article',
            name='topic',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dispatch.Topic'),
        ),
        migrations.AddField(
            model_name='user',
            name='person',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='person', to='dispatch.Person'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
