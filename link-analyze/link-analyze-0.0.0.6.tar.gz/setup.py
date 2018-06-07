#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : pengjun.pj

from setuptools import setup, find_packages

setup(
    name='link-analyze',
    version='0.0.0.6',
    description='for link theft analyze, input url , output theft url',
    author='peter',
    author_email='peter517@126.com',
    url='',
    py_modules=['link-analyze'],
    install_requires=[
        "openpyxl >= 2.4.9", "selenium>=3.7.0","scapy>=2.3.2"
    ],
    python_requires=">=2.6, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    license='GPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    entry_points={'console_scripts': [
        'link-analyze = link_analyze.main:main']},
)
