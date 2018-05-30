from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='defpi',
    version='18.05.01',
    description='Python module for dEF-Pi',
    long_description=long_description,
    author='Maarten Kollenstart',
    author_email='maarten.kollenstart@tno.nl',
    install_requires=['protobuf', 'pyxb', 'requests'],
    python_requires='~=3.5',
    packages=["defpi", "defpi.common", "defpi.protobufs"]
)
