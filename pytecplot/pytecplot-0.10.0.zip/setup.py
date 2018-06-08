from __future__ import print_function

import os
import platform
import re
import sys
from codecs import open
from os import path
from subprocess import Popen, PIPE
from textwrap import dedent


def long_description():
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here,'README.rst'), encoding='utf-8') as f:
        return f.read()

def read_version():
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here,'tecplot','version.py'), encoding='utf-8') as f:
        m = re.search(r"version = '(.*?)'",f.read(),re.M)
        return m.group(1)

def install_requires():
    req = ['six', 'pyzmq', 'flatbuffers']
    if sys.version_info < (3,0):
        req.append('future')
        req.append('contextlib2')
    if sys.version_info < (3,4):
        req.append('enum34')
    return req

def test_requires():
    req = ['coverage']
    if sys.version_info < (3,3):
        req.append('mock')
    return req

def extra_requires():
    return ['numpy', 'ipython', 'pillow']

def doc_requires():
    req = ['sphinx', 'sphinxcontrib-napoleon']
    if sys.version_info < (3,3):
        req.append('mock')
    return req

def setup_opts():
    from setuptools import find_packages
    opts = dict(
        name='pytecplot',
        version=read_version(),
        description='A python interface to Tecplot 360',
        long_description=long_description(),
        #url='http://www.tecplot.com/pytecplot',
        url='http://www.tecplot.com/docs/pytecplot',
        author='Tecplot, Inc.',
        author_email='support@tecplot.com',
        #license='',
        classifiers=[
            # Development Status
            #   1 - Planning
            #   2 - Pre-Alpha
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Science/Research',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Topic :: Education',
            'Topic :: Multimedia :: Graphics :: 3D Rendering',
            'Topic :: Multimedia :: Graphics :: Presentation',
            'Topic :: Multimedia :: Graphics :: Viewers',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Topic :: Scientific/Engineering :: Mathematics',
            'Topic :: Scientific/Engineering :: Physics',
            'Topic :: Scientific/Engineering :: Visualization',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'License :: Other/Proprietary License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
        ],
        keywords= [
            'tecplot',
            'cfd',
            'data analysis',
            'scientific',
            'scientific computing',
            'statistics',
            'visualization',
            'numerical simulation',
            'aerospace',
        ],
        packages=find_packages(exclude=['test', 'test*']),
        install_requires=install_requires(),
        extras_require={
            'extras' : extra_requires(),
            'doc' : doc_requires(),
            'test' : test_requires(),
            'all' : extra_requires() + doc_requires() + test_requires(),
        },
    )
    return opts

if __name__ == '__main__':
    import struct

    if sys.version_info[:2] < (2, 7):
        raise Exception('PyTecplot only supports Python versions 2.7 and 3.4+')

    pointer_size = struct.calcsize('P')
    if pointer_size != 8:
        err = '{} bit architecture detected.\n'.format(pointer_size * 8)
        err += 'PyTecplot must be used with a 64-bit version of Python.'
        raise Exception(err)

    from setuptools import setup
    setup(**setup_opts())
