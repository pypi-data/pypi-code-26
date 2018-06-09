#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages


with open('README.md', 'r') as fh:
    long_description = fh.read()


setup(
    name='coinmarketcap-client',
    version='2.5.3',
    description='Python Coin Market Cap Client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Paula Grangeiro',
    author_email='contato@paulagrangeiro.com.br',
    url='https://gitlab.com/pgrangeiro/python-coinmarketcap-client',
    download_url='https://gitlab.com/pgrangeiro/python-coinmarketcap-client/-/archive/master/python-coinmarketcap-client-master.tar.gz',
    license='GNU General Public License v3.0',
    python_requires='>=3.6',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['requests>=2.18', ],
    keywords=['coinmarketcap', 'cryptocurrency', 'cryptocoin'],
    classifiers=[],
)
