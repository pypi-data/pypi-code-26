# -*- coding:utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='sxysdk',
    packages=find_packages(),
    version="0.0.11",
    description="sxy python sdk",
    author="shenxiaoyang",
    author_email="380944919@infocore.cn",
    license="GPLv3",
    url='https://github.com/shenxiaoyang/sxysdk-python.git',
    download_url='https://github.com/shenxiaoyang/sxysdk-python.git',
    keywords=['sdk'],
    classifiers=[],
    zip_safe=False,
    install_requires=[
        'cx_Oracle>=6.2.1',
        'paramiko>=2.4.1'
    ],
    include_package_data=True,
)