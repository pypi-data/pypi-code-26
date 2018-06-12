from __future__ import absolute_import, unicode_literals

import re

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


def make_password():
    return User.objects.make_random_password(length=16)


class LocalUrlValidator(RegexValidator):
    message = "URL must start with '/' and cannot contain spaces or special characters"
    regex = re.compile(
        "^/"        # Start with slash
        "[\w%/-]*"  # Allow letters and numbers, %, /, and -
        "$"         # End
    )


@python_2_unicode_compatible
class PasswordProtectedUrl(models.Model):
    """
    A URL that should be protected by a password.
    """
    url = models.CharField("URL", max_length=255, unique=True, validators=[LocalUrlValidator()])
    username = models.CharField("Username", max_length=50)
    password = models.CharField("Password", max_length=50, default=make_password)

    class Meta:
        verbose_name = "protected URL"
        verbose_name_plural = "protected URLs"

    def __str__(self):
        return self.url
