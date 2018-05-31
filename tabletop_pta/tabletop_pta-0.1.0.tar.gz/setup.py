#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'numpy>=1.13',
    'pyaudio>= 0.2',
    'scipy>=0.19',
    'matplotlib>=2.0',
]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Jeffrey Shafiq Hazboun",
    author_email='jeffrey.hazboun@nanograv.org',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Python Package to do Time of Arrival calculations for a Pulsar Timing Array demmo with metronomes.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='tabletop_pta',
    name='tabletop_pta',
    packages=find_packages(include=['tabletop_pta']),
    setup_requires=setup_requirements,
    scripts=['bin/PTAdemo_single_metronome','bin/PTAdemo_double_metronome'],
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/nanograv/tabletop_pta',
    version='0.1.0',
    zip_safe=False,
)
