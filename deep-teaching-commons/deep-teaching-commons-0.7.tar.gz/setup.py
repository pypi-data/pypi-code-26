#!/usr/bin/env python3

from setuptools import setup

setup(
    name='deep-teaching-commons',
    version='0.7',
    description='A Python module for common functionality across notebooks and teaching material.',
    author='Christoph Jansen, Benjamin Voigt',
    author_email='Christoph.Jansen@htw-berlin.de, Benjamin.Voigt@htw-berlin.de',
    url='https://gitlab.com/deep.TEACHING/deep-teaching-commons',
    packages=[
        'deep_teaching_commons',
        'deep_teaching_commons.data',
        'deep_teaching_commons.data.text',
        'deep_teaching_commons.data.fundamentals',
        'deep_teaching_commons.graphs'
    ],
    license='MIT',
    platforms=['any'],
    install_requires=[
        'requests',
        'networkx',
        'pydot',
        'pandas'
    ]
)
