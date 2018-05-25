import sys
from setuptools import setup, find_packages

NAME = "pi-util"
VERSION = "0.0.0"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools


setup(
    name=NAME,
    version=VERSION,
    description="python utility package on initial stage",
    author="Zeeshan",
    author_email="zeeshan.emallates@gmail.com",
    url="https://github.com/masked-runner/pi-util",
    keywords=["utility", "types", "lodash", "pydash", "pip", "pip-util", "util", "underscore"],
    # install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True
)


