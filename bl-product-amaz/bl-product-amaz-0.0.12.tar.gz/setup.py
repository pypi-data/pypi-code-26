# coding: utf-8

"""
    bl-product-amz
    Utility package for bl-product-amaz(DB)

"""

import sys
from setuptools import setup, find_packages

NAME = "bl-product-amaz"
VERSION = "0.0.12"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["pymongo"]

setup(
    name=NAME,
    version=VERSION,
    description="bl-product-amaz",
    author_email="lion@bluehack.net",
    url="",
    keywords=["BlueLens", "bl-product-amaz"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    """
)
