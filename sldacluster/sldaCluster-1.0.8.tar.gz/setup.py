# -*- coding: UTF-8 -*-
# author: liuyang
# date: 2018/5/29
# time: 下午12:17

from __future__ import print_function
from distutils.core import setup
from setuptools import find_packages, setup
# 库名 / 版本 / 描述 / 项目地址 / 作者 / 作者邮箱 / 协议 / 关键词 / 模块列表
# setup(name="python",
#       version="1.0",
#       description="my python",
#       url='',
#       author="liuyang",
#       author_email='1716401503@qq.com',
#       license='MIT',
#       keywords='python',
#       packages = ['sldaCluster'],
#       package_dir = {'sldaCluster':'sldaCluster'},
#       package_data = {'sldaCluster':['profile/*']},
#       py_modules=['sldaCluster.tfidf', 'sldaCluster.word2vec', 'sldaCluster.sldaModel', 'sldaCluster.Main']
#       )
NAME = 'sldaCluster'
DESCRIPTION = 'A cluster method that uses the classifier mind.'
URL = ''
EMAIL = '1716501503@qq.com'
AUTHOR = 'liuyang'
REQUIRES_PYTHON = '>=3.5.0'
VERSION = '1.0.8'
long_description = 'see the README.rst'
REQUIRED = ''

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    # long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(),
    package_dir={'sldaCluster':'sldaCluster'},
    package_data={'sldaCluster':['*']},
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],

)