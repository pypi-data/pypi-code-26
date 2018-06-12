from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ratlog',
    version='0.1.1',
    description=':rat: Ratlog Python library - Application Logging for Rats, Humans and Machines',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/alxwrd/ratlog.py',
    author='Alex Ward',
    author_email='alxwrd@googlemail.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    keywords='logging logger logs logging-library ratlog rats python-logger python-logging',
    packages=['ratlog'],
    project_urls={
        'Source': 'https://github.com/alxwrd/ratlog.py',
        'Bug Reports': 'https://github.com/alxwrd/ratlog.py/issues',
    },
)
