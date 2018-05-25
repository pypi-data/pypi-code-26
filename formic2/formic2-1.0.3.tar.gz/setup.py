###############################################################################
# Formic: An implementation of Apache Ant FileSet globs
# Copyright (C) 2012, Aviser LLP, Singapore.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from setuptools import setup
from os import path


def read(fname):
    """Loads the contents of a file, returning it as a string"""
    return open(path.join(path.dirname(__file__), fname)).read()


setup(
    name='formic2',
    version=read(path.join("formic", "VERSION.txt")),
    description='An implementation of Apache Ant FileSet and Globs',
    long_description=read("README.rst"),
    author='Aviser LLP, Singapore; wolfhong',
    author_email='hongxucai1991@gmail.com',
    url='https://github.com/wolfhong/formic',
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
    keywords=[
        'Apache Ant', 'glob', 'recurse', 'FileSet', 'file utilities', 'find', 'fnmatcher'
    ],
    license='GPLv3+',
    packages=["formic"],
    python_requires='>=2.6, <4',
    package_data={"formic": ["*.txt"]},
    entry_points={
        'console_scripts': ['formic = formic.command:entry_point'],
    },
)
