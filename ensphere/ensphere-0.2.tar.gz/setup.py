#!/usr/bin/env python2

from setuptools import setup
import os
import codecs
import re

#Copied from wheel package
here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(os.path.dirname(__file__), 'ensphere', '__init__.py'),
                 encoding='utf8') as version_file:
    metadata = dict(re.findall(r"""__([a-z]+)__ = "([^"]+)""", version_file.read()))

long_desc = "".join(open("README.md").readlines())

setup(name='ensphere',
      version=metadata['version'],
      description='Add XMP metadata for PanoSphere in the pictures.',
      long_description=long_desc,
      long_description_content_type="text/markdown",
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        ],
      author='Masakazu Matsumoto',
      author_email='vitroid@gmail.com',
      url='https://github.com/vitroid/ensphere/',
      keywords=['ensphere','panorama', 'equirectangular', 'photosphere', 'XMP' 'metadata'],
      license='MIT',
      packages=['ensphere'],
      install_requires=['python-xmp-toolkit', 'imagesize'],
      entry_points = {
              'console_scripts': [
                  'ensphere = ensphere.__main__:main'
              ]
          }
      )

