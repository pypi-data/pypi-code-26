from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='SwiftViperGenerator',

    version='1.1.0',

    description='VIPER boilerplate code generator for Swift XCode projects',
    long_description='',

    url='http://github.com/bivanov/swiftvipergenerator',

    author='Bohdan Ivanov',
    author_email='bogdanivanov@live.com',
    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Utilities',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',	 
    ],
    keywords='build development',

    packages=find_packages(exclude=['tests']),

    include_package_data=True,

    install_requires=['pbxproj', 'jinja2', 'pyyaml', 'colorama'],

    entry_points={
        'console_scripts': [
            'swivigen=swivigen:main',
        ],
    },
)
