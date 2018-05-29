#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: Put package requirements here

]

setup_requirements = [
    # TODO(ybbaigo): Put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: Put package test requirements here
    "jieba","scikit-learn","tensorflow==1.1.0","numpy","scipy","nltk","pandas"
]

setup(
    name='sklearn_plus',
    version='0.0.1',
    description="A set of python modules for Natural Language Processing",
    long_description=readme,
    author="Yuwen Yan",
    author_email='ybbaigo@gmail.com',
    url='https://github.com/ybbaigo/sklearn-plus',
    packages=find_packages(include=['sklearn_plus']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='sklearn_plus',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
