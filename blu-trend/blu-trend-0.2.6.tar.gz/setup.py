# coding: utf-8

"""
    blu-trend

    This is a package for get trend

    OpenAPI spec version: 0.2.6
    Contact: originman@bluehack.net
"""

from setuptools import setup, find_packages

NAME = "blu-trend"
VERSION = "0.2.6"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["selenium",
            "chromedriver_binary"]

setup(
    name=NAME,
    version=VERSION,
    description="get trend package",
    author_email="originman@bluehack.net",
    url="",
    keywords=["blu", "blu-trend"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    """
)
