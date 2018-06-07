""" Setup script. Used by easy_install and pip. """

import os
import sys
import subprocess as sp
import re

from setuptools import setup, find_packages, Command

VERSIONFILE="wrappers/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RunTimeError("Unable to find version string in {}.".format(VERSIONFILE))

#-----------------------------------------------------------------------------
# check python version. we need > 2.5, <3.x
if  sys.hexversion < 0x02050000 or sys.hexversion >= 0x03000000:
    raise RuntimeError("%s requires Python 2.x (2.5 or higher)" % name)


#-----------------------------------------------------------------------------
#
def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


#-----------------------------------------------------------------------------
setup_args = {
    'name'             : "extasy.wrappers",
    'version'          : verstr,
    'description'      : "EXTASY Project - Wrappers",
    'long_description' : (read('README.md') + '\n\n' + read('CHANGES.md')),
    'author'           : "The EXTASY Project",
    'url'              : "https://bitbucket.org/extasy-project/extasy-project",
    'download_url'     : "https://bitbucket.org/extasy-project/wrappers/get/"+verstr+".tar.gz",
    'license'          : "BSD",
    'classifiers'      : [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        'Topic :: System :: Distributed Computing',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix'
    ],

    'namespace_packages': ['wrappers'],
    'packages'    : find_packages('.'),
    'package_dir' : {'': '.'},
    'scripts' : [],
    'install_requires' : [],
    'zip_safe'         : False,
}

#-----------------------------------------------------------------------------

setup (**setup_args)
