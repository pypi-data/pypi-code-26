#!/usr/bin/env python

from setuptools import setup, find_packages

requirements = [
    'Jinja2',
    'mutagen',
    'pyyaml',
    'validators',
],

setup(
    name='pypodcaster',
    version='2.0.4',
    install_requires=requirements,
    packages=find_packages(exclude=("tests",)),
    url='http://github.com/mantlepro/pypodcaster',
    license='GPL-3.0',
    author='mantlepro',
    author_email='mantlepro@gmail.com',
    description='Generate podcast xml feed from a directory of media files',
    package_data={'pypodcaster': ['templates/*']},
    entry_points = {
        'console_scripts': ['pypodcaster = pypodcaster.__main__:main']
    }
)
