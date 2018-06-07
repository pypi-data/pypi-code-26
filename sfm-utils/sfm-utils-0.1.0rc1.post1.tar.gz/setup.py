#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


def readme():
    return read('README.rst')


def version():
    return read('sfm_utils', 'VERSION').strip()


setup(name='sfm-utils',
      version=version(),
      description='utilities for working with lexicography data '
          'encoded using Standard Format Markers (SFM data files).',
      long_description=readme(),
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Intended Audience :: Science/Research',
        'Topic :: Text Processing :: Linguistic',
        'Operating System :: OS Independent',
        'Environment :: Console'
      ],
      keywords='SFM MDF SIL lexicon lexicography expressivelogic',
      url='https://gitlab.com/bbsg/sfm_utils',
      project_urls={},
      author='Gavin Falconer',
      author_email='gfalconer@expressivelogic.co.uk',
      license='MIT',
      packages=['sfm_utils'],
      entry_points = {
        'console_scripts': ['sfm-sniffer=sfm_utils.sfm_sniffer:main'],
      },
      install_requires=[
          'docopt',
          'six'
      ],
      python_requires='>=3',
      include_package_data=True,
      zip_safe=False)
