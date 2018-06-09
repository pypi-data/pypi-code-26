#!/usr/bin/env python3

from setuptools import setup

setup(
    name="hclib",
    py_modules=["hclib"],
    version="0.1.25",
    description="A library to connect to https://hack.chat/",
    long_description=open("./README.md").read(),
    url="https://gitlab.com/neelkamath/hclib",
    author="Neel Kamath",
    author_email="neelkamath@icloud.com",
    license="MIT",
    keywords="hack.chat library",
    install_requires=["websocket-client"]
)
