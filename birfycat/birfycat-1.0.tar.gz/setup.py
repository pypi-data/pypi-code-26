#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='birfycat',
    version='1.0',
    author='zzcdy',
    author_email='15302010010@fudan.edu.cn',
    url='https://www.birfied.com',
    description=u'Virtual cat',
    packages=['birfycat'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'birfycat=birfycat:main',
        ]
    }
)