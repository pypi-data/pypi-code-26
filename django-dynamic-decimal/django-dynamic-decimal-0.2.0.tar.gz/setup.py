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

from setuptools import setup, find_packages

setup(
  name='django-dynamic-decimal',
  version='0.2.0',
  url='https://git.pispalanit.fi/pit/django-dynamic-decimal',
  author='Harry Karvonen',
  author_email='harry.karvonen@pispalanit.fi',
  description='Django Dynamic Decimal field',
  packages=find_packages(),
  zip_safe=False,
  platforms='any',
  license='MIT',
  install_requires=[
    'Django',
  ],
)
