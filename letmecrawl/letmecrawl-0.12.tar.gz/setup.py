#!/usr/bin/env python
import os

from setuptools import setup

name = "letmecrawl"

rootdir = os.path.abspath(os.path.dirname(__file__))

# Restructured text project description read from file
long_description = open(os.path.join(rootdir, 'README.rst')).read()

# Build a list of all project modules
packages = []
for dirname, _, filenames in os.walk(name):
        if '__init__.py' in filenames:
            packages.append(dirname.replace('/', '.'))

package_dir = {name: name}

setup(
    name=name,
    version='0.12',
    description='let me crawl',
    long_description=long_description,
    url='https://github.com/montenegrodr/letmecrawl',
    author='Robson Montenegro',
    author_email='montenegrodr@gmail.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    download_url='https://github.com/montenegrodr/letmecrawl/archive/0.0.12.tar.gz',
    keywords='scraper crawler proxy',
    packages=packages,
    package_dir=package_dir,
    install_requires=['six'],
    include_package_data=True
)
