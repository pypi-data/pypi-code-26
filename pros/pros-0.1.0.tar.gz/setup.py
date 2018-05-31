#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='pros',
    version='0.1.0',

    author='orsinium',
    author_email='master_fess@mail.ru',

    description='UNIX pipeline on python and steroids',
    long_description=open('README.rst').read(),
    keywords='pipe pipeline chain tree cli',

    packages=['pros', 'pros.commands', 'pros.core'],
    requires=['jinja2', 'prompt_toolkit', 'PyYAML'],

    url='https://github.com/orsinium/pros',
    download_url='https://github.com/orsinium/pros/tarball/master',

    license='GNU Lesser General Public License v3.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries',
    ],
)
