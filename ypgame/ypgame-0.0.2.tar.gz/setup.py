# -*- coding: utf-8 -*-
# @Time    : 2018/6/14 07:30
# @Author  : 千と千寻
# @Email   : pp2677345028@gmail.com
# @File    : setup.py.py

import setuptools

'''
with open("README.md", "r") as fh:
    long_description = fh.read()
'''


setuptools.setup(
    name="ypgame",
    version="0.0.2",
    author="Allen Xu",
    author_email="pp2677345028@gamil.com",
    description='A simple 2D game engine base on pyglet',
    #long_description=long_description,
    #long_description_content_type="text/markdown",
    url='http://github.com/',
    packages=setuptools.find_packages(),
    install_requires=[
        'pyglet',
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ),
)

