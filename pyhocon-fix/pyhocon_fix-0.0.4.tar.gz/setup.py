from distutils.core import setup
from setuptools import setup, find_packages

PACKAGE = "pyhocon_fix"
NAME = "pyhocon_fix"
DESCRIPTION = "Fixed json escape of pyhocon"
AUTHOR = "Lin Deng"
AUTHOR_EMAIL = "ptreesptrees@gmail.com"
URL = "https://github.com/LeviDeng/pyhocon_fix"
#VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version="0.0.4",
    description=DESCRIPTION,
    # long_description=read("README.md"),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="Apache License, Version 2.0",
    url=URL,
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    zip_safe=False,
)