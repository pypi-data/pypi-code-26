# -*- coding: utf-8 -*-
import os

from django.core.exceptions import ValidationError
from django.db import models
from gettext import gettext as _
from hashlib import sha256

from model_utils.models import TimeStampedModel

from .settings import FILE_LIMIT, LIMITER, AUTH_USER_MODEL


def hash_upload(instance, filename):
    instance.image.open() # make sure we're at the beginning of the file
    contents = instance.image.read() # get the contents
    fname, ext = os.path.splitext(filename)
    hasher = sha256()
    hasher.update(contents)
    return "{0}/{1}{2}".format(instance.owner_id, hasher.hexdigest(), ext)


class Image(TimeStampedModel):
    image = models.ImageField(verbose_name=_('Image'), upload_to=hash_upload, max_length=512)
    size = models.IntegerField(verbose_name=_('File size in bytes'), blank=True, editable=False)
    owner = models.ForeignKey(AUTH_USER_MODEL)

    def validate_size(self):
        self.size = self.image.size
        if self.size > FILE_LIMIT:
            raise ValidationError(_('File too large'))
        limit = LIMITER(self.owner)
        total = Image.objects.filter(owner=self.owner).aggregate(total=models.Sum('size'))['total'] or 0
        if limit < total + self.size:
            raise ValidationError(_('Limit exceed'))

    def clean(self):
        super(Image, self).clean()
        self.validate_size()

    def save(self, *args, **kwargs):
        self.size = self.image.size
        super(Image, self).save(*args, **kwargs)
