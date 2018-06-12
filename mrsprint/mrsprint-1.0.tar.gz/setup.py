# python
# -*- coding: utf-8 -*-

import os
import re
import sys

sys.path.insert(0, os.path.abspath('.'))

import mrsprint as pkg_project
from setuptools import setup


classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: Python']

requires = ['numpy>=1.13',
            'nmrglue>=0.6',
            'scipy>=1.1',
            'h5py>=2.8',
            'pyqtgraph>=0.10',
            'pyopengl>=3.1']

setup(name=pkg_project.package,
      version=pkg_project.__version__,
      description=pkg_project.description,
      author=pkg_project.authors_string,
      author_email=pkg_project.emails_string,
      packages=['mrsprint',
                'mrsprint.system',
                'mrsprint.simulator',
                'mrsprint.sequence',
                'mrsprint.subject',
                'mrsprint.gui'],
      classifiers=classifiers,
      entry_points={"gui_scripts": ["mrsprint=mrsprint.__main__:main"]},
      install_requires=requires,
      )
