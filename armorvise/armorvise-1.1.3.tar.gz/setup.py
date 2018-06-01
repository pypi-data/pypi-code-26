#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages
import json
import os

INFO_JSON = "conf.json"
NOW_PATH = os.path.abspath(os.path.dirname(__file__))
EXT_PATH = "{}/src/process/ext".format(NOW_PATH)

proj_info = json.loads(open(os.path.join(EXT_PATH, INFO_JSON)).read())

with open('README.rst', mode='r') as fd:
	long_description = fd.read()
    

setup(
    name = proj_info["name"], ### the same as console_scripts's name
    author = proj_info["author"],
    author_email = proj_info["author_email"],
    url = proj_info["url"],
    license = proj_info["license"],
    version = proj_info["version"],
    description = proj_info["description"],
	long_description = long_description,
    keywords = proj_info["keywords"],
    platforms = proj_info["platforms"],

    packages = find_packages('src'),
    package_dir = {'' : 'src'},
    include_package_data = True,
    entry_points = {
        'console_scripts':proj_info["console_scripts"],
        'gui_scripts':proj_info["gui_scripts"]
    }
)



