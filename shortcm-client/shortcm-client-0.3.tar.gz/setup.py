#!/usr/bin/env python

import setuptools
from distutils.core import setup

setup(name='shortcm-client',
      version='0.3',
      description='Short.cm commpand line UI',
      author='Andrii Kostenko',
      author_email='andrii@short.cm',
      url='https://github.com/Short-cm/shortcm-cli',
      packages=['shortcm_client'],
      long_description_content_type="text/markdown",
      long_description=open('README.md').read(),
      scripts=[
        'scripts/shortcm',
      ],
      requires=['requests'],
      entry_points={
        'console_scripts': [
            'shortcm=shortcm_client.__main__:main',
        ]
      }
 )
