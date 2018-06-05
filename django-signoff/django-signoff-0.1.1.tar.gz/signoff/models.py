# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, Q, Prefetch
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel


class DocumentConsent(TimeStampedModel):
    document = models.ForeignKey('Document',
                                 related_name="consents",
                                 on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    ip = models.GenericIPAddressField(
        help_text=_("The IP address from which the document was signed."),
    )

    xff_header = models.CharField(
        max_length=255,
        null=True, blank=True,
        help_text=_("The X-Forwarded-For header sent when the document was "
                    "signed."),
    )

    signed_name = models.TextField(
        help_text=_("The name entered in the signature box when the user "
                    "signed this document."),
    )


class DocumentQuerySet(models.QuerySet):
    def only_active(self):
        return self.filter(
            Q(next_version__isnull=True) |
            Q(next_version__required_by__gt=timezone.now())
        )

    def with_user(self, user):
        """
        Prefeteches DocumentConsent objects for the specified user to the
        key "user_consents".
        """

        kwargs = {}
        if hasattr(settings, 'SIGNOFF_CHECK_DOCUMENT_UPDATED') and\
           settings.SIGNOFF_CHECK_DOCUMENT_UPDATED:
            kwargs['created__gte'] = F('document__modified')
        if hasattr(settings, 'SIGNOFF_CHECK_FULL_NAME') and\
           settings.SIGNOFF_CHECK_FULL_NAME:
            kwargs['signed_name'] = user.get_full_name()

        return self.prefetch_related(Prefetch(
            "consents",
            queryset=DocumentConsent.objects.filter(
                user=user,
                **kwargs
            ),
            to_attr="user_consents",
        ))


class Document(TimeStampedModel):
    code = models.CharField(
        max_length=16,
        help_text=_("A short code, like 'tos' or 'privacy', used to identify "
                    "the various types of documents."),
    )

    prev_version = models.OneToOneField(
        "Document",
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='next_version',
        help_text=_("The previous revision of this document. Only the most "
                    "recent revision of each document code will be active at "
                    "any given time."),
    )

    name = models.CharField(
        max_length=255,
        help_text=_("Name of this document."),
    )

    details = models.TextField(
        help_text=_("A description of this document, about one paragraph "
                    "in length. Explain what the document is, and why the "
                    "user should review it."),
    )

    text = models.TextField(
        help_text=_("The text of this document, HTML is OK."),
    )

    required_by = models.DateTimeField(
        help_text=_("The time that this document must be signed by. After "
                    "this date, the document will be considered 'required' "
                    "by the django-consent middleware, and logged-in users "
                    "will need to sign it before being able to browse your "
                    "site."),
    )

    order = models.IntegerField(
        default=1000,
        help_text=_('An integer used to sort the list of Documents'),
    )

    objects = DocumentQuerySet.as_manager()

    class Meta:
        ordering = ['order']
