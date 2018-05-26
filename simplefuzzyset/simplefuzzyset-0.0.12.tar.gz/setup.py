import os
import sys
import platform

here = os.path.dirname(__file__)

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

#if sys.version_info[0] < 3 and sys.version_info[1] < 7:
#    requirements.append('importlib')

extra_kwargs = {}

ext_files = []

from setuptools import setup, Extension

setup(
    name = "simplefuzzyset",
    version = "0.0.12",
    author = "Theodore Morin",
    author_email = "morinted@gmail.com",
    description = ("A simpler python fuzzyset implementation."),
    license = "BSD",
    keywords = "fuzzyset fuzzy data structure",
    url = "https://github.com/morinted/fuzzyset/",
    packages=['simplefuzzyset'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],
    **extra_kwargs
)
