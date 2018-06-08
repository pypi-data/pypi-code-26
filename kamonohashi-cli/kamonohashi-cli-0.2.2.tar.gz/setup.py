# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages

VERSION = '0.2.2'

setup(
    name='kamonohashi-cli',
    version=VERSION,
    description='KAMONOHASHI Command Line Tool',
    long_description='',
    author='NS Solutions Corporation',
    author_email='kamonohashi-support@jp.nssol.nssmc.com',
    url='https://github.com/KAMONOHASHI/kamonohashi-cli',
    license='Apache License 2.0',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'click',
        'terminaltables',
        'kamonohashi-sdk',
        'requests',
        'six'
    ],
    dependency_links=[],
    entry_points={
        'console_scripts': ['kqi = kqicli.__main__:kqi_main']
    },
    zip_safe=False
)
