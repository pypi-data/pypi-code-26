# -*- coding: utf-8 -*-
"""
Created on Thu May 24 08:34:02 2018

@author: Hans_wang
@email: hans_wang@outlook.com
"""


import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="GTquant",
    version="0.0.1",
    author="GTedu",
    author_email="hans_wang@outlook.com",
    description="GT strategy backtesting framework",
    long_description=long_description,
    long_description_content_type="",
    url="http://www.gfedu.cn/class/aqf/",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft",
    ),
)
