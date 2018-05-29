#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'typing-tools'
DESCRIPTION = 'Provides tools for typing in Python 3.6.'
URL = 'https://gitlab.com/Hares/typing-tools'
EMAIL = 'ussx-hares@yandex.ru'
AUTHOR = 'Peter Zaitcev / USSX Hares'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = None

# What packages are required for this module to be executed?
REQUIRED = \
[
]

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(here, NAME.replace('-', '_'), '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):

        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source distribution…')
        cmd = '"{0}" setup.py sdist'.format(sys.executable)
        print(cmd)
        code = os.system(cmd)
        assert code == 0, "Build failed"

        self.status('Uploading the package to PyPi via Twine…')
        code = os.system("twine upload dist/{0}-*.tar.gz".format(NAME))
        assert code == 0, "Failed to push to the PyPi"

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        code = os.system('git push --tags')
        assert code == 0, "Failed to push to the git"

        sys.exit()


# Where the magic happens:
setup \
(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=[ 'typing_tools' ],
    # entry_points={ 'console_scripts': ['mycli=typing_tools:cli'], },
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    classifiers=
    [
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
