#!/usr/bin/env python

from setuptools import setup
from sphinx_rigado_theme import __version__

setup(
    name='sphinx_rigado_theme',
    version=__version__,
    author='Spencer Williams',
    author_email='spencer.williams@rigado.com',
    description='A Sphinx theme for Rigado',
    url='https://git.rigado.com/documentation/sphinx-rigado-theme',
    packages=['sphinx_rigado_theme'],
    # See http://www.sphinx-doc.org/en/stable/theming.html#distribute-your-theme-as-a-python-package
    entry_points = {
      'sphinx.html_themes': [
        'sphinx_rigado_theme = sphinx_rigado_theme',
      ]
    },
)
