#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='naivepyrunner',
      version='0.2.0',
      description='Naive timed execution of custom handlers in multiple threads',
      long_description=readme(),
      long_description_content_type='text/markdown',
      keywords='schedule scheduling cron timing parallel',
      classifiers=[
        'Development Status :: 7 - Inactive',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities'
      ],
      python_requires='>=3.5',
      url='http://github.com/henningjanssen/naivepyrunner',
      author='Henning Janßen',
      author_email='development@henning-janssen.net',
      license='MIT',
      packages=['naivepyrunner'],
      install_requires=[],  # built-ins only
      zip_safe=False)
