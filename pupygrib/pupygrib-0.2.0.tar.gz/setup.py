"""Build and install pupygrib."""

import io

from setuptools import setup, find_packages


with io.open('README.md', encoding='utf-8') as stream:
    long_description = stream.read()

setup(
    name='pupygrib',
    version='0.2.0',
    description='A light-weight pure Python GRIB reader',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://notabug.org/mjakob/pupygrib',
    author='Mattias Jakobsson',
    author_email='mattias.jakobsson@smhi.se',
    license='GPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='grib grid data meteorology',

    packages=find_packages(exclude=['tests*']),
    install_requires=['numpy', 'six'],
    extras_require={
        'dev': ['check-manifest', 'flake8', 'pytest-cov', 'tox'],
    },
)
