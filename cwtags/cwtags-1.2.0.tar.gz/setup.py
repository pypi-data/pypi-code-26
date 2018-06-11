#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0404,W0622,W0704,W0613
# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Generic Setup script, takes package info from __pkginfo__.py file.
"""
from __future__ import absolute_import
__docformat__ = "restructuredtext en"

from os.path import join, dirname

from setuptools import find_packages, setup

here = dirname(__file__)

# load metadata from the __pkginfo__.py file so there is no risk of conflict
# see https://packaging.python.org/en/latest/single_source_version.html
pkginfo = join(here, 'cwtags', '__pkginfo__.py')
__pkginfo__ = {}
with open(pkginfo) as f:
    exec(f.read(), __pkginfo__)
# get required metadatas
version = __pkginfo__['version']
license = __pkginfo__['license']
description = __pkginfo__.get('description')
web = __pkginfo__['web']
author = __pkginfo__['author']
author_email = __pkginfo__['author_email']
classifiers = __pkginfo__.get('classifiers')

requires = {}
for entry in ("__depends__", ):
    requires.update(__pkginfo__.get(entry, {}))
install_requires = [
    "{0} {1}".format(d, v and v or "").strip() for d, v in requires.items()
]

setup(
    name='cwtags',
    version=version,
    license=license,
    description=description,
    author=author,
    author_email=author_email,
    url=web,
    classifiers=classifiers,
    packages=find_packages(exclude=['test']),
    install_requires=install_requires,
    include_package_data=True,
    zip_safe=False,
)
