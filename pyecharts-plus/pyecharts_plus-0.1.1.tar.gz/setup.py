# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="pyecharts_plus",
    version="0.1.1",
    description="Some charts which pyecharts don't contain",
    long_description=open('README.rst').read(),
    author='Ijustwantyouhappy',
    author_email='18817363043@163.com',
    maintainer='',
    maintainer_email='',
    license='MIT',
    packages=find_packages(),
    platforms=["all"],
    url='',
    install_requires=["pandas>=0.22.0",
                      "pyecharts>=0.5.3"],
    classifiers=[
        "Environment :: Web Environment",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=True,
)