#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open
from setuptools import setup, find_packages
import platform

VERSION = '0.1.0a14'

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules'
]

with open('README.rst', 'r', encoding='utf-8') as f:
    README = f.read()
with open('HISTORY.rst', 'r', encoding='utf-8') as f:
    HISTORY = f.read()

if platform.system() == "Windows":
    dependancies = "monitoring/tools/modeldatacollector/lib/native/Windows/*"
elif platform.system() == "Darwin":
    dependancies = "monitoring/tools/modeldatacollector/lib/native/Darwin/*"
else:
    dependancies = "monitoring/tools/modeldatacollector/lib/native/Linux/*"

setup(
    name='azureml-monitoring',
    version=VERSION,
    description='Microsoft Azure Machine Learning Python SDK for collecting model data during operationalization',
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    author='Microsoft Corporation',
    author_email='amlmodeltracking@microsoft.com',
    url='',
    classifiers=CLASSIFIERS,
    keywords='azure machinelearning model operationalization datacollection',
    install_requires=[],
    packages=find_packages(),
    package_data={
        'azureml': [dependancies]
    }
)
