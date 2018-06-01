#!/usr/bin/env python
#This file is part of numword.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

import os
import re
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_version():
    init = read(os.path.join('escpos', '__init__.py'))
    return re.search("__version__ = '([0-9.]*)'", init).group(1)

setup(name='escpos',
    version=get_version(),
    author='Oscar Alvarez',
    author_email='oscar.alvarez.montero@gmail.com',
    url="http://www.bitbucket.org/presik/python_escpos/",
    description="Python library to manipulate ESC/POS Printers",
    download_url="http://www.bitbucket.org/presik/python_escpos/",
    packages=find_packages(),
    test_suite='escpos.tests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Printing',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    license='LGPL',
    use_2to3=True)
