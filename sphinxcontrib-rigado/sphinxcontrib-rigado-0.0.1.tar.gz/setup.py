#!/usr/bin/env python

from io import open
from setuptools import setup
from sphinxcontrib.rigado import __version__

setup(
    name='sphinxcontrib-rigado',
    version=__version__,
    author='Spencer Williams',
    author_email='spencer.williams@rigado.com',
    description='Sphinx extensions for Rigado',
    long_description=open('README.rst', encoding='utf-8').read(),
    url='https://git.rigado.com/documentation/sphinx',
    license='MIT',
    packages=['sphinxcontrib.rigado'],
    include_package_data=True,
)
