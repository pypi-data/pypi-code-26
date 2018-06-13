#!/usr/bin/env python
from setuptools import setup
setup(
  name = 'cs.sh',
  description = 'Convenience functions for constructing shell commands.',
  author = 'Cameron Simpson',
  author_email = 'cs@cskk.id.au',
  version = '20180613',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Development Status :: 4 - Beta', 'Intended Audience :: Developers', 'Operating System :: OS Independent', 'Topic :: Software Development :: Libraries :: Python Modules', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'],
  entry_points = {'console_scripts': ['shqstr = cs.sh:main_shqstr']},
  install_requires = [],
  keywords = ['python2', 'python3'],
  long_description = 'Functions for safely constructing shell command lines from bare strings.\nSomewhat like the inverse of the shlex stdlib module.',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.sh'],
)
