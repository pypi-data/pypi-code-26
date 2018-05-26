# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='dayli-client',
    version='2.1.1',
    description='API Client para facturación electrónica',
    license = 'DAYLISOFT',
    long_description=open('README.rst').read(),
    author='Daylisoft',
    author_email='daylisoft@gmail.com',
    url='https://daylisoft.com.ec/',
    packages=['daylifact'],
    install_requires=[
        'lxml==4.2.0',
        'requests==2.18.4',
    ],
    classifiers=[
        #https://packaging.python.org/tutorials/distributing-packages/
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2.7'
    ],
    keywords=['facturacion', 'client', 'daylisoft', 'sri', 'electronica', 'offline']
)