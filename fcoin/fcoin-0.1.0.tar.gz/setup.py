# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import codecs
import os
import fcoin

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

long_desc = """

FCoin API
===============

Fcoin data API. 



Install
--------------

    pip install fcoin
    
Upgrade
---------------

    pip install fcoin --upgrade
    
    
"""


setup(
    name='fcoin',
    version=fcoin.__version__,
    description='fcoin api',
#     long_description=read("READM.rst"),
    long_description = long_desc,
    author='wt',
    author_email='',
    license='Apache 2.0',
    url='',
    keywords='Crypto Asset api',
    classifiers=['Development Status :: 4 - Beta',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'License :: OSI Approved :: BSD License'],
    packages=find_packages(),
    package_data={'': ['*.csv']},
)