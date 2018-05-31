#!/usr/bin/env python
# coding=utf-8

from setuptools import find_packages, setup

setup(
    name='WQ_SDK',
    version=1.0,
    description=(
        'WangQing Python SDK。'
    ),
    long_description=open('README.rst').read(),
    author='gdky005',
    author_email='741227905@qq.com',
    maintainer='gdky005',
    maintainer_email='741227905@qq.com',
    license='BSD3 License',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/gdky005/WQPythonSDK',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
)