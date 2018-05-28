import os
import sys
from distutils.core import setup


def read(fname):
    """
    define 'read' func to read long_description from 'README.txt'
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='Django-EventAggregator',
    version='1.5.0',
    author='songtao',
    author_email='975765671@qq.com',
    url='https://pypi.org/project/Django-EventAggregator/',
    license='MIT',
    description='Event Aggregator for Django project',
    long_description=read('README.txt'),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords='django event',
    packages=['EventAggregator']
)

# command: python setup.py register sdist upload
