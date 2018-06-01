from setuptools import setup
import os
setup(
    name='globuslite',
    version='0.2.0',
    author='Landon T. Clipp',
    author_email='clipp2@illinois.edu',
    packages=['globuslite'],
    description='A lightweight interface to the Globus SDK.',
    long_description='globuslite provides a lightweight interface \
    to the Globus data transfer services. Normally, users must manually \
    implement the Globus API authentication flow, however this \
    package abstracts that away from users and manages authorization \
    tokens automatically. It also provides a simple way to submit transfer \
    tasks to Globus.',
    install_requires=[ 'configobj' ],
    url='https://github.com/TerraFusion/globuslite',
    keywords = ['globus', 'sdk', 'api', 'data', 'transfer', 'lite',
        'lightweight', 'light', 'globuslite'],
)

