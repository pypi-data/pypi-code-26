#!/usr/bin/env python3

from setuptools import setup

readme = open('README.md').read()

setup(
    name = 'django-shts3',
    version = '4.2',
    description = "Start Django dev server faster",
    long_description = readme,
    long_description_content_type='text/markdown',
    author = "Nikita Khabarov",
    author_email = "nikita.khabarov.al@gmail.com",
    url = "https://github.com/wolphin/django-shts3",
    py_modules = ['django_shts3'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    entry_points={
        'console_scripts': [
            'django = django_shts3:main',
            'd = django_shts3:main',
        ]
    },
)
