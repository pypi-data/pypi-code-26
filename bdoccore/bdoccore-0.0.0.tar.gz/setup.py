# -*- coding: utf-8 -*-
# pylint: disable=broad-except
"""bdoccore module can be installed and configured from here"""

from os import path
from setuptools import setup, find_packages
try:
    from bdocutils.files import read_file
    from bdocutils.files import path_format
except ImportError as err:
    raise Exception(
        ("ERROR: need to install first bdocutils"
         ", 'pip install bdocutils'"))


VERSION = "0.0.0"
CURR_PATH = "{}{}".format(path.abspath(path.dirname(__file__)), '/')


def read(file_name=None, is_encoding=True, ignore_raises=False):
    """Read file"""
    if file_name is None:
        raise Exception("File name not provided")
    return read_file(
        is_encoding=is_encoding,
        ignore_raises=ignore_raises,
        file_path=path_format(
            file_path=CURR_PATH,
            file_name=file_name,
            ignore_raises=ignore_raises))


setup(
    name='bdoccore',
    version=VERSION,
    license=read("LICENSE", is_encoding=False, ignore_raises=True),
    packages=find_packages(exclude=['tests']),
    description='Black Desert core library for private modules',
    long_description=read("README.rst"),
    author='Netzulo Open Source',
    author_email='netzuleando@gmail.com',
    url='https://github.com/RealImperialGames/BDOC-core.git',
    download_url=("https://github.com/RealImperialGames/"
                  "BDOC-core/tarball/v{}").format(
        VERSION),
    keywords=[
        'BlackDesert',
        'BlackDesertOnline',
        'Black',
        'Desert',
        'Online',
        'BDO',
        'game',
        'mmorpg',
        'Community',
        'bdoc-core',
        'bdoccore'
    ],
    install_requires=[
        'appdirs',
        'packaging==16.8',
        'pyparsing',
        'six==1.10.0',
        'nose==1.3.7',
        'nose-testconfig==0.10',
        'pytest',
        'wget',
        'bdocutils'
    ],
    setup_requires=[
        'pytest-runner',
        'tox',
    ],
    tests_require=[
        'pytest-html',
        'pytest-dependency',
        'pytest-cov',
        'pytest-benchmark',
        'pytest-benchmark[histogram]'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
)
