#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version():
    with open('VERSION', 'r') as f:
        version_str = f.read().strip()
    assert version_str
    return version_str


setup(
    name='telega-compose',
    version=get_version(),
    description='Utility to render docker-compose files with different states',
    long_description=open('README.rst', 'r').read(),
    author='Django Stars',
    author_email='alexander.ryabtsev@djangostars.com',
    url='https://github.com/django-stars/telega-compose',
    packages=['telega_compose'],
    entry_points="""
    [console_scripts]
    tcompose=telega_compose.main:cli
    """,
    install_requires=open('requirements.txt', 'r').readlines(),
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ]
)
