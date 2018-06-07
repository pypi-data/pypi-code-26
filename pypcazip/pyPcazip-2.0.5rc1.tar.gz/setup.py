#!/usr/bin/env python
"""  Setup script. Used by easy_install and pip. """

from __future__ import absolute_import, print_function, division

import os
import sys
import re
import textwrap


"""Some functions for checking and showing errors and warnings."""
def _print_admonition(kind, head, body):
    tw = textwrap.TextWrapper(initial_indent='   ', subsequent_indent='   ')

    print(".. {0}:: {1}".format(kind.upper(), head))
    for line in tw.wrap(body):
        print(line)


def exit_with_error(head, body=''):
    _print_admonition('error', head, body)
    sys.exit(1)


def print_warning(head, body=''):
    _print_admonition('warning', head, body)


def check_import(pkgname, pkgver):
    """ Check for required Python packages. """
    try:
        mod = __import__(pkgname)
        if mod.__version__ < pkgver:
            raise ImportError
    except ImportError:
        exit_with_error("Can't find a local {0} installation with version >= {1}. "
                        "Pypcazip needs {0} {1} or greater to compile and run! "
                        "Please read carefully the ``README`` file.".format(pkgname, pkgver))

    print("* Found {0} {1} package installed.".format(pkgname, mod.__version__))
    globals()[pkgname] = mod


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


"""Discover the package version"""
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
VERSIONFILE = "pypcazip/pcazip/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RunTimeError("Unable to find version string in {}.".format(VERSIONFILE))


"""Check Python version"""
print("* Checking Python version...")
if sys.version_info[:2] < (2, 7) or (3, 0) <= sys.version_info[0:2] < (3, 4):
    exit_with_error("You need Python 2.7 or 3.4+ to install pyPcazip!")
print("* Python version OK!")


"""Check minimum versions of NumPy, SciPy, Cython required."""
min_numpy_version = '1.0.3'
min_scipy_version = '0.10.0'
min_Cython_version = '0.19.0'

check_import('numpy', min_numpy_version)
check_import('scipy', min_scipy_version)
check_import('Cython', min_Cython_version)


"""Set up pyPcazip."""
from setuptools import setup, find_packages
from setuptools import Extension as Ext
class Extension(Ext, object):
    pass
from Cython.Build import cythonize

setup_args = {
    'name':             "pyPcazip",
    'version':          verstr,
    'description':      "PCA-based molecular dynamics trajectory file compression and analysis.",
    'long_description': "PCA-based molecular dynamics trajectory file compression and analysis.",
    'author':           "The University of Nottingham & BSC",
    'author_email':     "charles.laughton@nottingham.ac.uk",
    'url':              "https://bitbucket.org/ramonbsc/pypcazip/overview",
    'download_url':     "https://bitbucket.org/ramonbsc/pypcazip/get/{}.tar.gz".format(verstr),
    'license':          "BSD license.",

    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix'
    ],

    'packages': find_packages('pypcazip'),
    'package_dir': {'': 'pypcazip'},

    'scripts': ['scripts/pyPcazip',
                'scripts/pyPcaunzip',
                'scripts/pyPczcomp',
                'scripts/pyPczdump',
                'scripts/pyPczplot',
                'scripts/pyPczclust'],

    'install_requires': ['numpy',
                         'scipy',
                         'cython',
                         'mdtraj',
                         'argparse',
                         'six',
                         'networkx',
                         'pandas'],

    'zip_safe': False,

    'ext_modules':  cythonize(Extension(
                        name='MDPlus.fastfitting',
                        sources=['pypcazip/MDPlus/fastfitting/fastfitting.pyx'],
                        include_dirs=[numpy.get_include()]))
}

setup(**setup_args)
