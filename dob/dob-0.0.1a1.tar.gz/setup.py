#!/usr/bin/env python

from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='dob',
    version='0.0.1.a1',
    description='A cuddly, furry, powerful personal journal and professional time tracker.',
    long_description=readme,
    author='Hot Off The Hamster',
    author_email='hotoffthehamster@gmail.com',
    url='https://github.com/hotoffthehamster/dob',
    license='MIT',
    packages=['dob'],
    extras_require={
        'dev': [
            'flake8',
            'flake8-import-order',
            'tox-travis',
            'pytest',
            'pytest-cov',
            'coveralls',
            'wheel',
        ]
    }
)
