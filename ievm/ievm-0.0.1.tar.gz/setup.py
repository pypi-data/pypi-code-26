# -*- coding: utf-8 -
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ievm',
    version='0.0.1',
    description='tool for downloading IE VMs with checksum',
    long_description=long_description,
    url='https://github.com/zenixls2/ievm',
    author='Zenix Huang',
    author_email='zenixls2@gmail.com',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Monitoring',
        'Topic :: Internet',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            'ievm = ievm.__main__:main'
        ]
    },
    keywords='ie vm InternetExplore',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['requests'],
)
