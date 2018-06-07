#!/usr/bin/env python

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup( name='clewareADC',
       version='0.2',
       author='Johannes Koch',
       author_email='johannes@ortsraum.de',
       description='Python module to read values from Cleware USB-ADC 2',
       long_description=read('README.rst'),
       license='MIT',
       keywords=['cleware', 'adc', 'hidapi'],
       classifiers=[ 'Development Status :: 5 - Production/Stable',
                     'Intended Audience :: Science/Research',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: MIT License',
                     'Programming Language :: Python',
                     'Topic :: Home Automation',
                     'Topic :: Scientific/Engineering' ],
       url='https://gitlab.com/darkforce/clewareADC',
       download_url='https://gitlab.com/darkforce/clewareADC/-/archive/0.2/clewareADC-0.2.tar.gz',
       packages=['clewareADC'],
       install_requires=['hidapi'],
     )

