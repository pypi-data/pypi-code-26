#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from thumbor_focus_filter import __version__

tests_require = [
    'mock',
    'nose',
    'coverage',
    'yanc',
    'colorama',
    'preggy',
    'ipdb',
    'coveralls',
    'numpy',
]

setup(
    name='thumbor_focus_filter',
    version=__version__,
    description='Focus filter for thumbor.',
    long_description='''
Focus filter for thumbor.
''',
    keywords='thumbor filter',
    author='sport1.de',
    author_email='paolo.garri@sport1.de',
    url='https://github.com/sport1online/thumbor-focus-filter',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pillow',
    ],
    extras_require={
        'tests': tests_require,
    }
)
