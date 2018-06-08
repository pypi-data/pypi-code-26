# -*- coding: utf-8 -*-

from os.path import join, dirname
from setuptools import setup

def read( fname ):
    return open( join( dirname( __file__ ), fname ), encoding = 'UTF-8' ).read()

requires = read( 'requirements.txt' ).splitlines()
long_description = read( 'README.rst' )

setup(
    name = 'metslesliens',
    version = '1.3.0',
    author = 'Seb35',
    author_email = 'seb35pypi0@seb35.fr',
    description = 'Mets des liens entre articles d’un texte de loi français.',
    license = 'WTFPL',
    platforms = 'Any',
    keywords = [ 'law', 'legal', 'legalese', 'france' ],
    url = 'https://framagit.org/parlement-ouvert/metslesliens',
    packages = [ 'metslesliens' ],
    package_data = { '' : [ '*.txt' ]},
    requires = requires,
    install_requires = requires,
    long_description = long_description,
    zip_safe = True,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: French',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Text Processing :: Linguistic',
    ],
)
