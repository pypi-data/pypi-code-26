#!/usr/bin/env python
from __future__ import print_function  
from setuptools import setup, find_packages  
import sys 

setup(
    name = "raw2clean",
    version = "1.0.1",
    packages = ['raw2clean'],
    author="Yong Deng",
    author_email = "yodeng@tju.edu.cn",
    description = "QC for rawdata without adapter",
    url="https://github.com/yodeng/raw2clean",
    license="MIT",
    entry_points = {
        'console_scripts': [  
            'raw2clean = raw2clean.raw2clean:main',
            'sumfq = raw2clean.summary_fastq:main'
        ]
    }

)

