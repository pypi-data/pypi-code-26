# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.db import models, router

from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from django_useful_things.signals import post_safe_delete, pre_safe_delete


class SoftDeleteModelQuerySet(models.QuerySet):
    def delete(self, user_disabled=None, force_delete=False):
        if force_delete:
            return super(SoftDeleteModelQuerySet, self).delete()
        return self.update(is_active=False, user_disabled=user_disabled)


class SoftDeleteModelManager(models.Manager):
    def __init__(self, queryset_cls=None, only_active=True):
        self.only_active = only_active
        self._queryset_cls = queryset_cls
        super(SoftDeleteModelManager, self).__init__()

    def get_queryset(self):
        base = super(SoftDeleteModelManager, self).get_queryset()
        if self.only_active:
            return base.filter(is_active=True)
        return base


class SoftDeleteModel(TimeStampedModel):
    is_active = models.BooleanField(_(u'Ativo'), default=True)
    date_disable = models.DateTimeField(null=True)
    user_disabled = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True,
                                      verbose_name=_('Quem desativou'), related_name='disabled_%(class)s')

    objects = SoftDeleteModelManager.from_queryset(SoftDeleteModelQuerySet)(only_active=True)
    all_objects = SoftDeleteModelManager.from_queryset(SoftDeleteModelQuerySet)(only_active=False)

    def delete(self, user_disabled=None, force_delete=False, using=None, *args, **kwargs):
        using = using or router.db_for_write(self.__class__, instance=self)
        if force_delete:
            return super(SoftDeleteModel, self).delete(*args, **kwargs)
        if self.is_active:
            pre_safe_delete.send(
                sender=self.__class__, instance=self, using=using
            )
            self.is_active = False
            self.date_disable = now()
            self.user_disabled = user_disabled
            post_safe_delete.send(
                sender=self.__class__, instance=self, using=using
            )
        return super(SoftDeleteModel, self).save()

    def active(self, commit=True, **kwargs):
        if not self.is_active:
            self.is_active = True
            self.date_disable = None
        if commit:
            return super(SoftDeleteModel, self).save(**kwargs)

    class Meta:
        abstract = True


class AddressModel(TimeStampedModel):
    street = models.CharField(_(u'Logradouro'), max_length=128, blank=True)
    number = models.CharField(_(u'Numero'), max_length=16, blank=True)
    complement = models.CharField(_(u'Complemento'), max_length=64, blank=True)
    district = models.CharField(_(u'Bairro'), max_length=64, blank=True)
    city = models.CharField(_(u'Cidade'), max_length=64, blank=True)
    state = models.CharField(_(u'Estado'), max_length=64, blank=True)
    zip_code = models.CharField(_(u'CEP'), max_length=10, blank=True)

    @staticmethod
    def format_address(parts, last_part=None):
        result = u", ".join(filter(lambda x: x, parts))
        if last_part is None:
            return result
        return u' - '.join(filter(lambda x: x, [result, last_part]))

    def get_simple_address(self):
        return self.format_address([self.street, self.number, self.complement], self.district)

    def get_full_address(self):
        return self.format_address([self.street, self.number, self.complement, self.city, ], self.state)

    class Meta:
        verbose_name = _(u'Endereço')
        verbose_name_plural = _(u'Endereços')
        abstract = True

    def __str__(self):
        return self.get_full_address()


class WeekDayModelMixin(TimeStampedModel):
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(0, 7)
    WEEKDAY_CHOICES = (
        (MONDAY, _("Segunda-feira")),
        (TUESDAY, _("Terça-feira")),
        (WEDNESDAY, _("Quarta-feira")),
        (THURSDAY, _("Quinta-feira")),
        (FRIDAY, _("Sexta-feira")),
        (SATURDAY, _("Sábado")),
        (SUNDAY, _("Domingo")),
    )
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES, verbose_name=_('Dia da semana'))

    def __str__(self):
        return self.get_weekday_display()

    class Meta:
        abstract = True
