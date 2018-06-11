from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='justml',
    version='1.0.1',
    description='JustML client library',
    long_description=long_description,
    url='https://justml.io',
    author='JustML',
    author_email='hello@justml.io',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='justml ml machinelearning datascience',
    packages=find_packages(exclude=[]),
    install_requires=['requests']
)
