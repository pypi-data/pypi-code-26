import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

setup(name='templatio',
    version='0.1.1',
    packages = find_packages(),
    include_package_data=True,
    description='Convert text files based on input and output templates',
    long_description = README,
    author='Marco Bellaccini',
    url='https://github.com/marcobellaccini/templatio',
    license='Apache License 2.0',
    scripts=['bin/templatio'],
    install_requires=['textfsm','Jinja2'],
    keywords = "convert text template TextFSM Jinja2",
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
)
