#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

requirements = [
    'djangorestframework>=3.8.2',
    'ai-django-core>=1.1.7'
]

setup(
    name='ai-drf-core',
    version='1.0.0',
    author=u'Ambient Innovation: GmbH',
    author_email='hello@ambient-innovation.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://gitlab.ambient-innovation.com/ai/ai-drf-core.git',
    license="The MIT License (MIT)",
    description='Lots of helper functions and useful widgets for the django REST Framework.',
    long_description=open('README.md').read(),
    zip_safe=False,
    install_requires=requirements
)
