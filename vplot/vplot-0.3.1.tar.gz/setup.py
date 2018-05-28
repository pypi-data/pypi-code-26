#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
from setuptools import setup

# Hackishly inject a constant into builtins to enable importing of the
# module. Stolen from `kplr`
import sys
if sys.version_info[0] < 3:
    import __builtin__ as builtins
else:
    import builtins
builtins.__VPLOT_SETUP__ = True
import vplot


def readme():
    """Get the long description from the README."""
    with open('README.rst') as f:
        return f.read()


# Setup!
setup(name='vplot',
      version=vplot.__version__,
      description='VPLANET Plotting Tools',
      long_description=readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Astronomy',
      ],
      url='https://bitbucket.org/bitbucket_vpl/vplanet/vplot/',
      author='Rodrigo Luger',
      author_email='rodluger@uw.edu',
      license='MIT',
      packages=['vplot'],
      install_requires=[
          'numpy',
          'matplotlib >= 1.4.0'
      ],
      include_package_data=True,
      package_data={},
      cmdclass={},
      scripts=['bin/vplot'],
      zip_safe=False)
