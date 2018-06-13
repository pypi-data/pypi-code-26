#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages

setup(
    name='bixin-oauth2',
    version='0.0.7',
    description='bixin oauth2 lib version',
    author='freeza91',
    author_email='useyes91@gmail.com',
    keywords=('Python', 'pyoauth2', 'bixin'),
    license='MIT License',
    url='https://github.com/haobtc/pyhaobtc/tree/master/haobtc_oauth2',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=['requests'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        ],
    zip_safe=False,
)
