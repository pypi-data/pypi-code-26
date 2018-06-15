# -*- coding: utf-8 -*-
# pylint: disable=broad-except
"""qautils module can be installed and configured from here"""

from os import path
from setuptools import setup, find_packages
from qautils.files import read


PACKAGE_NAME = 'qautils'
AUTHOR = "Netzulo SQA developer"
AUTHOR_EMAIL = "netzuleando@gmail.com"
DESCRIPTION = ("QA utils library provides"
               " methods compatibility with"
               " all python versions")
VERSION = "0.0.2"
CURR_PATH = "{}{}".format(path.abspath(path.dirname(__file__)), '/')
INSTALL_REQUIRES = []
SETUP_REQUIRES = [
    'pytest-runner',
    'tox',
]
TESTS_REQUIRE = [
    'pytest-html',
    'pytest-dependency',
    'pytest-cov',
    'pytest-benchmark',
    'pytest-benchmark[histogram]',
]
KEYWORDS = ['qautils', 'qa', 'files', 'json']
GIT_URL = "https://github.com/netzulo/qautils"
GIT_URL_DOWNLOAD = "{}/tarball/v{}".format(GIT_URL, VERSION)
LICENSE_FILE = read(
    file_path=CURR_PATH,
    file_name="LICENSE",
    is_encoding=False,
    ignore_raises=True)
README_FILE = read(
    file_path=CURR_PATH,
    file_name="README.rst")

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    license=LICENSE_FILE,
    packages=find_packages(exclude=['tests']),
    description=DESCRIPTION,
    long_description=README_FILE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=GIT_URL,
    download_url=GIT_URL_DOWNLOAD,
    keywords=KEYWORDS,
    install_requires=INSTALL_REQUIRES,
    setup_requires=SETUP_REQUIRES,
    tests_require=TESTS_REQUIRE,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
