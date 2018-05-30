# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _, get_language


class Control(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=False)
    updated_at = models.DateTimeField(auto_now=True, blank=False)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Country(Control):
    slug = models.CharField(max_length=255, blank=False, unique=True, editable=False)
    code2 = models.CharField(_('Código - alpha2'), max_length=2, blank=False, unique=True, default='')
    code3 = models.CharField(_('Código - alpha3'), max_length=3, blank=False, unique=True, default='')
    flag = models.FileField(_('Bandeira'), blank=True, null=True)
    geocode = models.IntegerField(_('Geocode'), null=True, blank=True, unique=True, default=0, editable=False)

    class Meta:
        verbose_name = _('País')
        verbose_name_plural = _('Paises')

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return u'%s' % self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.code2)
        return super(Country, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                         update_fields=update_fields)

    @property
    def name(self):
        try:
            country_translation = CountryTranslations.objects.get(country__pk=self.pk, lang=get_language())
            return country_translation.name
        except Exception as e:
            return self.code2


class CountryTranslations(Control):
    lang = models.CharField(max_length=10, choices=settings.LANGUAGES, verbose_name=_('Idioma'))
    country = models.ForeignKey(Country, blank=False, related_name='country_translation', verbose_name=_('Pais'))
    name = models.CharField(max_length=50, blank=False)

    class Meta:
        verbose_name = _('Nome do País')
        verbose_name_plural = _('Nome dos Paises')
        unique_together = (("lang", "country"),)

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return str(self.name)


class State(Control):
    country = models.ForeignKey(Country, blank=False, verbose_name=_('Pais'))
    code = models.CharField(max_length=50, verbose_name=_('Pais'))
    geocode = models.IntegerField(_('Geocode'), null=True, blank=True, unique=True, default=0, editable=False)

    class Meta:
        verbose_name = _('Estado')
        verbose_name_plural = _('Estados')

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return u'%s' % self.name

    @property
    def name(self):
        try:
            state_translation = StateTranslation.objects.get(state__pk=self.pk, lang=get_language())
            return state_translation.name
        except Exception as e:
            return unicode(str(self.geocode) + ' - ' + self.country.code2.upper())

    @property
    def translations(self):
        return [x.lang for x in StateTranslation.objects.filter(state=self).all()]


class StateTranslation(Control):
    lang = models.CharField(max_length=10, choices=settings.LANGUAGES)
    state = models.ForeignKey(State, blank=False, related_name='state_translation', verbose_name=_('Região/Estado'))
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = _('Nome Região/Estado')
        verbose_name_plural = _('Nome Regiões/Estados')
        unique_together = (("lang", "state"),)

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return u'%s' % self.name


class City(Control):
    state = models.ForeignKey(State, blank=False)
    geocode = models.IntegerField(_('Geocode'), null=True, blank=True, default=0, editable=False)
    latitude = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True)
    longitude = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True)

    class Meta:
        verbose_name = _('Cidade')
        verbose_name_plural = _('Cidades')

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return u'%s' % self.name

    @property
    def name(self):
        try:
            city_translate = CityTranslation.objects.get(city__pk=self.pk, lang=get_language())
            return city_translate.name
        except Exception:
            return unicode(u'cidade - %s, %s - %s' % (self.pk, self.state.code, self.state.country.code2))


class CityTranslation(Control):
    lang = models.CharField(max_length=10, choices=settings.LANGUAGES)
    city = models.ForeignKey(City, blank=False, related_name='city_translation', verbose_name=_('Cidade'))
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = _('Nome de Cidade')
        verbose_name_plural = _('Nomes de Cidades')
        unique_together = (("lang", "city"),)

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return u'%s' % self.name


class Location(Control):
    city = models.ForeignKey(City, verbose_name=_('Cidade'))
    neighborhood = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Bairro'))
    postal_code = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Código Postal'))
    address = models.CharField(max_length=255, blank=False, verbose_name=_('Endereço'))
    street_number = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Número'))
    complement = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Complemento'))
    latitude = models.CharField(max_length=255, verbose_name=_('Latitude'))
    longitude = models.CharField(max_length=255, verbose_name=_('Longitude'))
    slug = models.CharField(max_length=255, blank=False, unique=False)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.address
