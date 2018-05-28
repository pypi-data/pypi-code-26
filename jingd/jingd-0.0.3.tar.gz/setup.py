#! /usr/bin/env python
# coding: utf-8

#  __author__ = 'wangzhihao.sh'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys

if sys.version_info <= (2, 7):
    sys.stderr.write("ERROR: jingyun aliyun python sdk requires Python Version 2.7 or above.\n")
    sys.stderr.write("Your Python Version is %s.%s.%s.\n" % sys.version_info[:3])
    sys.exit(1)

name = "jingd"
version = "0.0.3"
url = "https://github.com/"
license = "MIT"
author = "wangzhihao.sh"
short_description = "jingd auth Service Library"
long_description = """Jingdu password Service."""
keywords = "jingd"
install_requires = ["requests"]

setup(name=name,
      version=version,
      author=author,
      author_email="zhouheng@gene.ac",
      url=url,
      packages=["jingd", "jingd/admin"],
      license=license,
      description=short_description,
      long_description=long_description,
      keywords=keywords,
      install_requires=install_requires,

      entry_points='''[console_scripts]
            jingd.usermod=jingd.usermod:main
            jingd.block=jingd.block:block_func
            jingd.unlock=jingd.unlock:unlock_func
            jingd.reset=jingd.reset:reset_func
      '''
      )