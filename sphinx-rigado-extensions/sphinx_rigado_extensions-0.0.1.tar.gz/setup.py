#!/usr/bin/env python

from io import open
from setuptools import setup
from sphinx_rigado_extensions import __version__

setup(
    name='sphinx_rigado_extensions',
    version=__version__,
    author='Spencer Williams',
    author_email='spencer.williams@rigado.com',
    description='Sphinx extensions for Rigado',
    long_description=open('README.rst', encoding='utf-8').read(),
    url='https://git.rigado.com/documentation/sphinx',
    license='MIT',
    packages=['sphinx_rigado_extensions'],
    include_package_data=True,
)
