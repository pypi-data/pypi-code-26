# -*- coding: utf-8 -*-

from __future__ import unicode_literals


from django.conf import settings
from django.utils.translation import ugettext_lazy as _


FROM_EMAIL = settings.DEFAULT_FROM_EMAIL

EMAIL_RECIPIENTS = getattr(settings, 'TIRRILEE_EMAIL_RECIPIENTS',
                           [settings.DEFAULT_FROM_EMAIL])

SUBJECT_INTRO = getattr(settings, 'TIRRILEE_SUBJECT_INTRO',
                        _("Message from contact form: "))

USE_HTML_EMAIL = getattr(settings, 'TIRRILEE_USE_HTML_EMAIL', True)