# -*- coding: utf-8 -*-
"""
Goodreads API Client
=====

Goodreads API Client is a non-official Python client for
`Goodreads <http://www.goodreads.com/>`.
"""
import ast
import re
from setuptools import setup, find_packages

_version_re = re.compile(r'VERSION\s+=\s+(.*)')

with open('goodreads_api_client/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

with open('README.rst', 'r') as f:
    readme = f.read()


def read_requires(group):
    with open('./requirements/{}.txt'.format(group)) as reqs_txt:
        return [line for line in reqs_txt]


docs_requires = read_requires('docs')
install_requires = read_requires('install')
publish_requires = read_requires('publish')
test_require = read_requires('test')

extras_require = {
    'docs': docs_requires,
    'publish': publish_requires,
    'test': test_require,
}

setup(
    name='goodreads_api_client',
    version=version,
    url='https://github.com/mdzhang/goodreads-api-client-python',
    author='Michelle D. Zhang',
    author_email='zhang.michelle.d@gmail.com',
    description='A non-official client for Goodreads (https://goodreads.com)',
    long_description=readme,
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
    ],
    packages=find_packages(),
    extras_require=extras_require,
    tests_require=test_require,
    install_requires=install_requires,
    test_suite='goodreads_api_client.tests',
    include_package_data=True,
    zip_safe=False,
    platforms=[],
)
