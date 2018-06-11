# -*- coding: utf-8 -*-
from setuptools import setup

requires = [
    'requests==2.18.4',
]

extras_require = {
    'test': [
        'pytest',
        'pytest-cov',
    ],
    'ci': [
        'python-coveralls',
    ]
}

setup(name='smart-fflags-client',
    version='0.0.2',
    description='Smart Dashboard to manage feature flags Client',
    author='Daniel Debonzi',
    author_email='debonzi@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    install_requires=requires,
    extras_require=extras_require,
    url='https://github.com/debonzi/smartflags-client.git',
    packages=['smartflags'],
    )
