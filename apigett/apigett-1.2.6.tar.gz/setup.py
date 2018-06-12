#!/usr/bin/env python
from setuptools import setup
import apigett

setup(name=apigett.NAME,
      version=apigett.VERSION,
      description=apigett.SHORT_DESCRIPTION,
      long_description=apigett.LONG_DESCRIPTION,
      url=apigett.APP_URL,
      author=apigett.AUTHOR,
      classifiers=["License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                   "Operating System :: Unix",
                   "Programming Language :: Python :: 3 :: Only",
                   "Topic :: Utilities",
                   "Development Status :: 4 - Beta",
                   "Environment :: Console",
                   "Natural Language :: English"],
      author_email=apigett.AUTHOR_EMAIL,
      license=apigett.LICENSE,
      packages=[apigett.NAME],
      install_requires=["requests"],
      entry_points={"console_scripts":["apigett=apigett:run"]},
      include_package_data=True,
      zip_safe=False)