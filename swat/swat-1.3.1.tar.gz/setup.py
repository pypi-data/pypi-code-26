#!/usr/bin/env python
# encoding: utf-8
#
# Copyright SAS Institute
#
#  Licensed under the Apache License, Version 2.0 (the License);
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

''' Install the SAS Scripting Wrapper for Analytics Transfer (SWAT) module '''

import glob
import os
import re
from setuptools import setup, find_packages

def md2rst_heading(match):
    ''' Convert markdown headings to rst headings '''
    rst_head = ['=', '-', '+', '#', '^']
    return '%s\n%s\n' % (match.group(2), rst_head[len(match.group(1))-1] * len(match.group(2)))

def md2rst(fname):
    ''' Simple markdown to rst converter '''
    data = open(os.path.join(os.path.dirname(__file__), fname)).read()
    return re.sub(r'^(#+)\s+(.*?)\s*$', md2rst_heading, data, flags=re.M)

try:
    README = md2rst('README.md')
except:
    README = 'See README.md'

if glob.glob('swat/lib/*/tk*'):
    LICENSE = 'Apache v2.0 (SWAT) + SAS Additional Functionality (SAS TK)'
else:
    LICENSE = 'Apache v2.0'

setup(
    zip_safe=False,
    name='swat',
    version='1.3.1',
    description='SAS Scripting Wrapper for Analytics Transfer (SWAT)',
    long_description=README,
    #long_description_content_type='text/markdown',
    author='SAS',
    author_email='Kevin.Smith@sas.com',
    url='http://github.com/sassoftware/python-swat/',
    license=LICENSE,
    packages=find_packages(),
    package_data={
        'swat': ['lib/*/*', 'tests/datasources/*'],
    },
    install_requires=[
        'pandas >= 0.16.0',
        'six >= 1.9.0',
        'requests',
    ],
    platforms='any',
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
    ],
)
