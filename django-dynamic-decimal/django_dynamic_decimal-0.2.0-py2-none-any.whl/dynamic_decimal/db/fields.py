#!/usr/bin/env python
# vi: et sw=2 fileencoding=utf-8

#============================================================================
# Django Dynamic Decimal
# Copyright (c) 2017 Pispalan Insinööritoimisto Oy (http://www.pispalanit.fi)
#
# All rights reserved.
# Redistributions of files must retain the above copyright notice.
#
# @description [File description]
# @created     16.04.2017
# @author      Harry Karvonen <harry.karvonen@pispalanit.fi>
# @copyright   Copyright (c) Pispalan Insinööritoimisto Oy
# @license     All rights reserved
#============================================================================

from __future__ import unicode_literals

import decimal

from django.db import models
from django.core import exceptions
from django import forms
from django.utils import (
  formats,
  six,
)
from django.utils.translation import ugettext_lazy as _


class DynamicDecimalField(models.CharField):

  empty_strings_allowed = False
  default_error_messages = {
    'invalid': _("'%(value)s' arvon täytyy olla desimaalinumero."),
  }
  description = "Dynamic decimal number"
  MAX_DIGITS = 20
  DECIMAL_PLACES = 10


  def __init__(self, verbose_name=None, name=None, **kwargs):
    if "max_length" not in kwargs:
      kwargs["max_length"] = 255

    super(DynamicDecimalField, self).__init__(verbose_name, name, **kwargs)
    # def __init__


  def clean(self, value, model_instance):
    value = self.to_python(value)

    if value is not None:
      self.validate(six.text_type(value), model_instance)
      self.run_validators(six.text_type(value))

    return value
    # def clean


  def from_db_value(self, value, expression, connection, context):
    # pylint: disable=unused-argument
    return self.to_python(value)
    # def from_db_value


  def to_python(self, value):
    if value is None:
      return value

    if isinstance(value, decimal.Decimal):
      return value

    if isinstance(value, six.text_type):
      value = formats.sanitize_separators(value).strip()

    try:
      return decimal.Decimal(value)
    except decimal.InvalidOperation:
      raise exceptions.ValidationError(
        "invalid value",
        code='invalid',
        params={'value': value},
      )
    # def to_python


  def get_prep_value(self, value):
    if value is None:
      return value

    return six.text_type(value)
    # def get_prep_value


  def formfield(self, form_class=None, **kwargs):
    # pylint: disable=arguments-differ, unused-argument
    defaults = {
      'max_digits': self.MAX_DIGITS,
      'decimal_places': self.DECIMAL_PLACES,
      'form_class': forms.DecimalField,
    }
    defaults.update(kwargs)
    # FIXME CharField yrittää antaa max_length argumentin, jota
    # forms.DecimalField ei tue. Joudutaan kutsumaan suoraan Field eikä
    # oikeaoppisesti super(DynamicDecimalField, self).formfield(**defaults)
    return models.Field.formfield(self, **defaults)


  # class DynamicDecimalField
