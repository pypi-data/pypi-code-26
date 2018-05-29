#!/usr/bin/env python3
"""Setup file for pip module."""

from setuptools import setup


with open('README.md') as f:
    DESCRIPTION = f.read()

setup(
    name='psd',
    version='1.1.4',
    description='Python tools for data visualization and spectral analysis.',
    long_description=DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://gitlab.in2p3.fr/j2b.bayle/psd',
    author='Jean-Baptiste Bayle (APC/CNRS/CNES)',
    author_email='bayle@apc.in2p3.fr',
    license='GNU GPLv3',
    packages=['psd'],
    install_requires=[
        'argparse',
        'numpy',
        'scipy',
        'matplotlib',
    ],
    entry_points={
        'console_scripts': ['psd=psd.psd:main'],
    },
    zip_safe=False,
)
