#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: JunWang
# Mail: shutupwj@163.com
# Created Time:  2018-6-7 22:08:34
#############################################

from setuptools import setup, find_packages

setup(
    name = "AutoEPD",
    version = "0.0.2",
    keywords = ("pip", "EPD","Environmental Product Declaration","sensitivity analysis","uncertainty analysis"),
    description = "A package for calculating the EPD",
    long_description = "A package for calculating the Environmental Product Declaration",
    license = "Apache License Version 2.0",

    url = "https://github.com/Jakkwj/autoepd",
    author = "JunWang",
    author_email = "shutupwj@163.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["matplotlib","numpy","pandas","psycopg2","seaborn","xlrd"]
)