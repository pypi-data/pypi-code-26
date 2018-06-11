#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='untappd_crawler',
    author='Arun Kumar Ramanathan',
    author_email='rako.aka.arun@gmail.com',
    license='MIT License',
    url='https://github.com/therako/untappd_crawler',
    description='A CLI client for exporting elasticsearch data to csv',
    long_description=README,
    version='0.2',
    packages=find_packages(exclude=('tests',)),
    cmdclass={'test': PyTest},
    scripts=('bin/untappd_crawler',),
    install_requires=[],
    tests_require=[
        'pytest',
        'mock==1.0.1'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
