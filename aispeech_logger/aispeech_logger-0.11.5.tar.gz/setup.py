# -*- coding: UTF-8 -*-
"""
File Name :    setup.py
Author :       unasm
mail :         unasm@sina.cn
Last_Modified: 2018-05-16 20:43:11
"""


from distutils.core import setup
from setuptools import setup, find_packages

__version__ = '0.11.5'

setup(
    name='aispeech_logger',
    version=__version__,
    keywords=('aispeech'),
    description='test for balogger',
    license='MIT License',
    author='jiamin.dou',
    author_email='jiamin.dou@aispeech.com',
    packages=["aispeech_logger"],
    #packages=find_packages(),
    platforms='any',
    url='http://www.unasm.com',      # 包的主页
    install_requires=[
        "kafka",
        "py_zipkin",
        "pytz",
        "uuid",
    ]
)
