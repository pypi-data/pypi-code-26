from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='docker-cmd',
    version='0.5.0',
    description='A builder for docker command strings',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=["test_*"]),
)
