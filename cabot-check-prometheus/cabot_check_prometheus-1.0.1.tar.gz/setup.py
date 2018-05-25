#!/usr/bin/env python

from setuptools import find_packages, setup

setup(name='cabot_check_prometheus',
      version='1.0.1',
      description='A Prometheus plugin for Cabot',
      author='Widen Enterprises',
      author_email='pgarland@widen.com',
      url='https://github.com/widen/cabot-check-prometheus',
      packages=find_packages(),
    )
