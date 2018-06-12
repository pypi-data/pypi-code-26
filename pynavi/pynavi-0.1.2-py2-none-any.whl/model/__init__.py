# -*- coding: utf-8 -*-
# Author: sunguangran (sunguangran@daixiaomi.com)
import datetime

from django.db import models


class BaseModel(models.Model):
    """ base model """

    class Meta:
        abstract = True

    @classmethod
    def get_model(cls, *args, **kwargs):
        try:
            return cls.objects.get(*args, **kwargs)
        except Exception as e:
            return None if not kwargs.__contains__('default') else kwargs.get('default')

    def to_json(self, fields=None):
        if fields is None:
            fields = []

        res = {}

        for field in fields:
            v = getattr(self, field)

            if isinstance(v, datetime.datetime):
                v = v.strftime('%Y-%m-%d %H:%M:%S')

            if v is None:
                v = ''

            res.update({field: v})

        return res
