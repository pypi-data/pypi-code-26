from django.db import models
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from gettext import gettext as _

from django_user_images.models import Image
from django_user_images.settings import FILE_LIMIT, LIMITER


class ImageSerializer(serializers.ModelSerializer):
    def validate_image(self, value):
        size = value.size
        owner = self.context.get('owner')

        if size > FILE_LIMIT:
            raise ValidationError(_('File too large'))

        limit = LIMITER(owner)
        total = Image.objects.filter(owner=owner).aggregate(total=models.Sum('size'))['total'] or 0
        if limit < total + size:
            raise ValidationError(_('Limit exceed'))
        return value

    class Meta:
        model = Image
        fields = '__all__'
        read_only_fields = ('owner',)
