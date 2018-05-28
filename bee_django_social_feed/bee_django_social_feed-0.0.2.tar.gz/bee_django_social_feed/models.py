# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings

# Create your models here.

class Feed(models.Model):
    publisher = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='发布者')
    content = models.TextField(verbose_name='内容')
    created_at = models.DateTimeField(auto_now_add=True)


class FeedComment(models.Model):
    feed = models.ForeignKey(Feed)
    comment = models.TextField(verbose_name='评论')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)


class FeedEmoji(models.Model):
    feed = models.ForeignKey(Feed)
    emoji = models.IntegerField(default=0, verbose_name='感受')  # 0 赞，1 笑趴，2 哇，3 心碎，4 怒
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
