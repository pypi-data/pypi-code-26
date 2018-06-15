"""
LED_Analyze - setup
Date: 15 June 2018
By: Ivan Pougatchev
Version: 1.0
"""
from setuptools import setup

setup(
    name="ledanalyze",
    description="Process colorimetry data",
    version="1.0",
    url="https://github.com/pougivan/LED_Analyze",
    author="pougivan",
    packages=["LED_Analyze"],
    install_requires=[
        "numpy",
        "matplotlib",
        "openpyxl",
        ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
        ))
