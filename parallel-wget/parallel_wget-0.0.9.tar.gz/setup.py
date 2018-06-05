"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.
setup(
    name='parallel_wget',  # Required
    version='0.0.9',  # Required
    description='Wget in parallel',  # Required
    long_description='Given a set of http URLs, fetch in parallel',  # Optional
    author='Aimee Barciauskas',  # Optional
    author_email='aimee@developmentseed.org',  # Optional
    keywords='wget multiprocessing parallel http https',  # Optional
    packages=find_packages(exclude=['.circleci', 'contrib', 'docs', 'tests']),
    py_modules=['parallel_wget'],
    install_requires=['wget'],  # Optional
)
