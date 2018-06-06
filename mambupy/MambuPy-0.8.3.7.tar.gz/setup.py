#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:license: GPLv3, see LICENSE for more details.
"""

import os, sys
import setuptools

VERSION = "0.8.3.7"


def readme():
    """print long description"""
    import m2r
    with open('MambuPy/README.md') as f:
        return m2r.convert(f.read())


class VerifyVersionCommand():
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')
        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(tag, VERSION)
            sys.exit(info)


setuptools.setup(name             = "MambuPy",
                 version          = VERSION,
                 description      = "A python lib for using Mambu APIs.",
                 long_description = readme(),
                 long_description_content_type = "text/markdown",
                 url              = "https://jstitch.gitlab.io/MambuPy.html/",
                 author           = "Javier Novoa C.",
                 author_email     = "jstitch@gmail.com",
                 license          = "GPLv3",
                 keywords         = ["mambu",],
                 packages         = ['MambuPy',],
                 python_requires  = '>=2.7',
                 cmdclass         = {'verify' : VerifyVersionCommand},
    )
