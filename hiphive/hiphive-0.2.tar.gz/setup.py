#!/usr/bin/env python

import re
import subprocess
import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 5, 0, 'final', 0):
    raise SystemExit('Python 3.5 or later is required!')

with open('README.rst', encoding='utf-8') as fd:
    long_description = fd.read()

with open('hiphive/__init__.py') as fd:
    lines = '\n'.join(fd.readlines())
try:
    git_label = subprocess.check_output(['git', 'describe',
                                         '--tags', '--bbrev=0'])
    version = git_label.strip().decode('utf-8')
except Exception:
    version = re.search("__version__ = '(.*)'", lines).group(1)
maintainer = re.search("__maintainer__ = '(.*)'", lines).group(1)
maintainer_email = re.search("__maintainer_email__ = '(.*)'", lines).group(1)
url = re.search("__url__ = '(.*)'", lines).group(1)
license = re.search("__license__ = '(.*)'", lines).group(1)
description = re.search("__description__ = '(.*)'", lines).group(1)

name = 'hiphive'  # PyPI name

# Linux-distributions may want to change the name:
if 0:
    name = 'python-hiphive'

setup(name=name,
      version=version,
      description=description,
      long_description=long_description,
      url=url,
      maintainer=maintainer,
      maintainer_email=maintainer_email,
      platforms=['unix'],
      install_requires=['ase',
                        'h5py',
                        'numba',
                        'numpy',
                        'sklearn',
                        'spglib',
                        'sympy'],
      packages=find_packages(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Topic :: Scientific/Engineering :: Physics'])
