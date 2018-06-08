import sys
import os
from os import path
from setuptools import setup, find_packages
from dropsonde import __version__

dirname = path.realpath(path.dirname(__file__))


def load_requirements(filename):
    with open(path.join(dirname, filename)) as f:
        return [l for l in f.read().strip().split('\n')
                if not l.startswith('-')]


reqs = []
reqs.extend(load_requirements('requirements.txt'))
readme = path.join(dirname, 'README.md')


setup(
    name='dropsonde',
    version=__version__,
    description='Compiled python generated from the Cloud Foundry Dropsonde Protobuf definition files',
    author='Adam Jaso',
    license='Apache License Version 2.0',
    long_description=open(readme).read(),
    packages=find_packages(),
    install_requires=reqs,
    url='https://github.com/hsdp/python-dropsonde'
)
