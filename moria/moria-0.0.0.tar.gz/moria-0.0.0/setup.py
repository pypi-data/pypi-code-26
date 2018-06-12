#!/usr/bin/python3
"""Setup script for moria."""
import os

from setuptools import find_packages, setup


def readme():
    """Return content of README file."""
    with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
        return f.read()


setup(name='moria',
      version='0.0.0',
      description='Just a placeholder for my intended app',
      long_description=readme(),
      author='Jan Musílek',
      author_email='jan.musilek@matfyz.cz',
      packages=find_packages(),
      classifiers=[
        'Development Status :: 1 - Planning',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
      ])
