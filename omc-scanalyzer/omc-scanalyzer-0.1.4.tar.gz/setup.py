# -*- coding: utf-8 -*-
 
 
"""setup.py: setuptools control."""
 
 
import re
from setuptools import setup
 
 
version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('omc_scanalyzer/main.py').read(),
    re.M
    ).group(1)
 
 
with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")
 
 
setup(
    name = "omc-scanalyzer",
    packages = ["omc_scanalyzer"],
    entry_points = {
        "console_scripts": ['omc_scanalyzer = omc_scanalyzer.main:main']
        },
    version = version,
    description = "A tool developed for analyzing OMC scans at LIGO",
    long_description = long_descr,
    author = "Alexei Ciobanu",
    author_email = "alexei.ciobanu95@gmail.com",
    )

