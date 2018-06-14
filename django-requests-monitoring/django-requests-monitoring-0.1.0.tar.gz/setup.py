from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-requests-monitoring',
    version='0.1.0',
    description='Manage http requests metrics via StatsD.',
    long_description=long_description,
    url='https://github.com/emilioag/django-requests-monitoring/',
    author='emilioag',
    author_email='emilioag@mail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='django statsd, monitoring',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'examples']),
    install_requires=[
        'Django==2.0',
        'datadog==0.21.0'
    ],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
)
