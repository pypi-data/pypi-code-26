import os
import re
import subprocess
from os.path import dirname, isdir, join
from setuptools import setup

version_re = re.compile('^Version: (.+)$', re.M)


def get_version():
    d = dirname(__file__)

    if isdir(join(d, '.git')):
        # Get the version using "git describe".
        cmd = 'git describe --tags --match [0-9]*'.split()
        try:
            version = subprocess.check_output(cmd).decode().strip()
        except subprocess.CalledProcessError:
            print('Unable to get version number from git tags')
            exit(1)

        # PEP 386 compatibility
        if '-' in version:
            version = '.post'.join(version.split('-')[:2])

    else:
        # Extract the version from the PKG-INFO file.
        with open(join(d, 'PKG-INFO')) as f:
            version = version_re.search(f.read()).group(1)

    return version

setup(
    name='appset',
    packages=['appset'],
    version=get_version(),
    description='A simple CLI made for use with external modules',
    author='mkubaczyk@apptension.com, mmlodzikowski@apptension.com',
    author_email='mkubaczyk@apptension.com, mmlodzikowski@apptension.com',
    url='https://github.com/apptension/appset',
    download_url='https://github.com/apptension/appset/archive/0.1.tar.gz',
    keywords=['cli', 'setup', 'modules'],
    classifiers=[],
    scripts=['bin/appset']
)
