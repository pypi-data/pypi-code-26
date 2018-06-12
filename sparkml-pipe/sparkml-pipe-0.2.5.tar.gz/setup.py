# -*- encoding: utf-8 -*-
import os
from setuptools import setup, find_packages

requirements = [
    "pyspark>=2.3.0",
    "PyYAML>=3.12",
]

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()


with open("sparkmlpipe/__version__.py") as fh:
    version = fh.readlines()[-1].split()[-1].strip("\"'")

setup(
    name='sparkml-pipe',
    description='A configurable PySpark pipeline library.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=version,
    packages=find_packages(exclude=['test']),
    install_requires=requirements,
    setup_requires=['setuptools>=38.6.0'],
    include_package_data=True,
    author='Michi Tech',
    author_email='parkerzf@gmail.com',
    license='BSD',
    platforms=['Linux'],
    classifiers=[],
    url='https://bitbucket.org/xtechai/sparkml-pipe')
