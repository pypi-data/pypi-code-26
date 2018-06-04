# -*- coding: utf-8 -*-
"""Setup file for the UdevBackup project.
"""


import codecs
import os.path
import re

from setuptools import setup, find_packages

# avoid a from udevbackup import __version__ as version (that compiles udevbackup.__init__)
version = None
for line in codecs.open(os.path.join('udevbackup', '__init__.py'), 'r', encoding='utf-8'):
    matcher = re.match(r"""^__version__\s*=\s*['"](.*)['"]\s*$""", line)
    version = version or matcher and matcher.group(1)

# get README content from README.md file
with codecs.open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as fd:
    long_description = fd.read()

entry_points = {'console_scripts': ['udevbackup = udevbackup.cli:main']}

setup(
    name='udevbackup',
    version=version,
    description='No description yet.',
    long_description=long_description,
    author='flanker',
    author_email='flanker@19pouces.net',
    license='CeCILL-B',
    url='',
    entry_points=entry_points,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='udevbackup.tests',
    install_requires=['termcolor', 'google_speech'],
    setup_requires=[],
    classifiers=['Development Status :: 3 - Alpha', 'Operating System :: POSIX :: Linux',
                 'License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3 :: Only'],
)
