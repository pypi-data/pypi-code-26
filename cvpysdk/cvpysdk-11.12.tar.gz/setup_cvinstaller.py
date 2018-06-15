# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# Copyright Commvault Systems, Inc.
# See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Setup file for the CVPySDK Python package."""

import os
import re
import ssl
import sys
import subprocess

from setuptools import setup, find_packages


ssl._create_default_https_context = ssl._create_unverified_context

ROOT = os.path.dirname(__file__)
VERSION = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')


def get_version():
    """Gets the version of the CVPySDK python package from __init__.py file."""
    init = open(os.path.join(ROOT, 'cvpysdk', '__init__.py')).read()
    return VERSION.search(init).group(1)


def readme():
    """Reads the README.rst file and returns its contents."""
    with open(os.path.join(ROOT, 'README.rst')) as file_object:
        return file_object.read()


def get_license():
    """Reads the LICENSE.txt file and returns its contents."""
    with open(os.path.join(ROOT, 'LICENSE.txt')) as file_object:
        return file_object.read()


setup(
    name='cvpysdk',
    version=get_version(),
    author='Commvault Systems Inc.',
    author_email='Dev-PythonSDK@commvault.com',
    description='Commvault SDK for Python',
    license=get_license(),
    long_description=readme(),
    url='https://github.com/CommvaultEngg/cvpysdk',
    scripts=[],
    packages=find_packages(),
    keywords='commvault, python, sdk, cv, simpana, commcell, cvlt, webconsole',
    include_package_data=True,
    zip_safe=False,
    project_urls={
        'Bug Tracker': 'https://github.com/CommvaultEngg/cvpysdk/issues',
        'Documentation': 'https://commvaultengg.github.io/cvpysdk/',
        'Source Code': 'https://github.com/CommvaultEngg/cvpysdk/tree/SP12'
    }
)


if 'win' in sys.platform.lower():
    PYTHON_PATH = sys.executable
    PIP_PATH = os.path.join(os.path.dirname(PYTHON_PATH), 'Scripts', 'pip')

    PACKAGES_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'packages')

    PYTHON_VERSION_FOLDER = 'PY{0}{1}'.format(
        str(sys.version_info.major), str(sys.version_info.minor)
    )

    PACKAGES = list(map(
        lambda x: os.path.join(PACKAGES_DIRECTORY, x) if x.endswith('.whl') else None,
        os.listdir(PACKAGES_DIRECTORY)
    ))

    PACKAGES_DIRECTORY = os.path.join(PACKAGES_DIRECTORY, PYTHON_VERSION_FOLDER)

    for package in os.listdir(PACKAGES_DIRECTORY):
        PACKAGES.append(os.path.join(PACKAGES_DIRECTORY, package))

    for package in PACKAGES:
        if package is None or os.path.isdir(package):
            continue

        TEMP_PROCESS = subprocess.Popen(
            [PIP_PATH, 'install', package],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )

        OUTPUT, ERROR = TEMP_PROCESS.communicate()

        if ERROR.decode():
            print(ERROR.decode())
            continue

        print(OUTPUT.decode())
