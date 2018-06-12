import os
import re
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'pyjsonassert', '__init__.py')) as f:
    version = re.compile(r".*__version__ = '(.*?)'", re.S).match(f.read()).group(1)

setup(
    name='pyJsonAssert',
    packages=find_packages(exclude=['tests']),
    version=version,
    description='Facilitates Json asserts in REST API testing',
    author='Javier Seixas',
    author_email='dev@javierseixas.com',
    license='MIT',
    url='https://github.com/javierseixas/pyJsonAssert',
    keywords=['json', 'api', 'testing', 'assert', 'assertion', 'comparing'],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License'
    ],
    install_requires=[
        'jsondiff>=1.1'
    ]
)