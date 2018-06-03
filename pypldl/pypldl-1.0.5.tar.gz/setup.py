#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
setup(
    name='pypldl',
    version='1.0.5',

    description='A crawler with parallel downloading',
    url=None,
    author='Benoît Ryder',
    author_email='benoit@ryder.fr',

    license='MIT',

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

    packages=find_packages(),
    install_requires=['beautifulsoup4', 'urllib3', 'html5lib'],

    entry_points={
        'console_scripts': [
            'pypldl=pypldl.cli:main',
        ],
        'gui_scripts': [
            'pypldl-gui=pypldl.gui:main'
        ],
    },
)
