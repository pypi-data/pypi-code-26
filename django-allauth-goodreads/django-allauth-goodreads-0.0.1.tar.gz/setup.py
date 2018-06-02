#!/usr/bin/env python
import io

from setuptools import setup, find_packages


long_description = io.open('README.md', encoding='utf-8').read()

METADATA = dict(
    name='django-allauth-goodreads',
    version='0.0.1',
    author='Stefan Wehrmeyer',
    author_email='mail@stefanwehrmeyer.com',
    description='Django applications addressing'
    'authentication with goodreads.com as a django-allauth module',
    long_description=long_description,
    url='https://github.com/stefanw/django-allauth-goodreads',
    keywords='django auth account social oauth goodreads registration',
    tests_require=[],
    install_requires=[
        'django-allauth',
        'xmltodict'
    ],
    include_package_data=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
        'Topic :: Internet',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
    ],
    packages=find_packages(),
)

if __name__ == '__main__':
    setup(**METADATA)
