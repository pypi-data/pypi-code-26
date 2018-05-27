import codecs
import os
import re

from setuptools import setup

def find_version(*file_paths):
    with open(os.path.join(os.path.dirname(__file__), *file_paths)) as file:
        version_file = file.read()

    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    long_description = readme.read()

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]

setup(
    name='grg-grgdata',
    packages=['grg_grgdata'],
    version=find_version('grg_grgdata', '__init__.py'),
    url='https://github.com/lanl-ansi/grg-grgdata',
    license='BSD',

    author='Carleton Coffrin',
    author_email='cjc@lanl.gov',

    install_requires=['tabulate', 'jsonschema'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest-cov'],
    test_suite='tests',
    description='Data structures and methods for reading and writing GRG data files',
    long_description=long_description,
    include_package_data=True,
    package_data={'grg_grgdata': ['schema/*.json']},
    classifiers = classifiers,
)