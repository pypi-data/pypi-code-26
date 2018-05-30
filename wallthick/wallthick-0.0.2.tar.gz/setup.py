#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import wallthick

import setuptools

with open('README.md') as readme_file:
    readme = readme_file.read()


setuptools.setup(
    name='wallthick',
    version=wallthick.__version__,
    description='PD8010 wall thickness calculations',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Ben Randerson',
    author_email='ben.m.randerson@gmail.com',
    url='https://github.com/benranderson/wallthick',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'wallthick=wallthick.cli:main',
        ],
    },
    include_package_data=True,
    install_requires=['Click>=6.0'],
    license='MIT License',
    zip_safe=False,
    keywords='wall thickness engineering pipelines',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Other Audience',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Operating System :: OS Independent",
    ],
    test_suite='tests',
)
