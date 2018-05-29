# coding: utf-8

"""
    XCover Expression Language
"""

from setuptools import setup, find_packages  # noqa: H301

NAME = "xcover_expression_language"
VERSION = "0.0.4"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "lark-parser==0.5.6"
]

setup(
    name=NAME,
    version=VERSION,
    description="A DSL that evaluates against Python API",
    author_email="",
    url="",
    keywords=["expression", "string expression", "XCover"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    A DSL that evaluates against Python API.
    """
)
