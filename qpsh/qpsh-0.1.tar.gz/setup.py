# coding: utf-8

from setuptools import setup


requires = []


setup(
    name='qpsh',
    version='0.1',
    description='Call shell commands from python shell.',
    url='https://github.com/TRSasasusu/qpsh',
    author='kaito kishi',
    author_email='trsasasusu@gmail.com',
    license='MIT',
    keywords='shell commands alias',
    packages=[
        "qpsh",
    ],
    install_requires=requires,
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Unix Shell',
        'Topic :: System :: Shells',
        'Topic :: System :: System Shells',
        'Operating System :: POSIX',
    ],
)
