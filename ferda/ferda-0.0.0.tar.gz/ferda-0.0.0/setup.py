#!/usr/bin/python3
"""Setup script for ferda."""
import os

from setuptools import find_packages, setup


def readme():
    """Return content of README file."""
    with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
        return f.read()


setup(name='ferda',
      version='0.0.0',
      description='Web admin interface for FRED',
      long_description=readme(),
      author='Jan Musílek',
      author_email='jan.musilek@nic.cz',
      packages=find_packages(),
      classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
      ])
