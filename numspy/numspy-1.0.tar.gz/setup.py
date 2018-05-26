import sys
from os import path
from shutil import rmtree
from codecs import open
from setuptools import setup, Command

# Package meta-data.
NAME = 'numspy'
DESCRIPTION = 'A python module for sending free sms as well as finding details of a mobile Number via website way2sms.'
URL = 'https://github.com/bhattsameer/numspy'
AUTHOR = 'Debugger'
VERSION = '1.0'

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email='UNKNOWN',
    url=URL,
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Communications',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    keywords='Numspy Way2sms freesms futuresms sms numspy',
    install_requires=['beautifulsoup4', 'bs4', 'requests', 'huepy'],
    packages=[
        'numspy',
    ],
)
