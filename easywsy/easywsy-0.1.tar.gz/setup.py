# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='easywsy',
    version='0.1',
    description='Simple Web Service development API based on suds',
    url='https://gitlab.e-mips.com.ar/infra/easywsy',
    author='Martín Nicolás Cuesta',
    author_email='cuesta.martin.n@hotmail.com',
    license='AGPL3+',
    packages=['easywsy'],
    install_requires=[
        'suds',
    ],
    zip_safe=False
)
