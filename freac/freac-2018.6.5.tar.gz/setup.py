#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='freac',
    version='2018.6.5',
    description='Converter from Frelon to Crysalis',
    author='Vadim Dyadkin',
    author_email='dyadkin@gmail.com',
    url='https://hg.3lp.cx/id11tb',
    license='GPLv3',
    install_requires=[
        'numpy',
        'cryio',
        'decor',
        'pyqtgraph',
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'freac=freac.__init__:freac',
            'inspecteur=freac.__init__:inspecteur',
        ],
    },
    py_modules=[
        'freac.ui.__init__',
        'freac.ui.qfreac',
        'freac.ui.qinspect',
        'freac.ui.resources_rc',
        'freac.__init__',
        'freac.wfreac',
        'freac.winspect',
    ],
)
