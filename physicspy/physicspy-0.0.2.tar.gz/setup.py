from setuptools import setup, find_packages
from codecs import open
from os import path

path = path.abspath(path.dirname(__file__))

with open('README.md') as file:
    long_description = file.read()

setup(name = 'physicspy',
      version = '0.0.2',
      license = 'MIT',
      author = 'Jorge A. Garcia',
      author_email = 'jorgeagr97@gmail.com',
      classifiers = ['Topic :: Scientific/Engineering :: Physics'],
      keywords = 'physics math science',
      description = 'Compilation of computational methods for use in Physics - Still Under Work!',
      packages = find_packages(exclude = ['tests']),
      install_requires = ['numpy'],
      python_requires='~=3.3',
      long_description = long_description,
      zip_safe = False,
      )
