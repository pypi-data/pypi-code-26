#!/usr/bin/env python3
from setuptools import setup 
import yxspkg_encrypt
setup(name='yxspkg_encrypt',   
      version=yxspkg_encrypt.__version__,    
      description='A simple API to encrypt data. Encrypt algorithm is based on linear congruence',    
      author=yxspkg_encrypt.__author__,    
      install_requires=['rsa'],
      py_modules=['yxspkg_encrypt'],
      platforms='any',
      author_email='blacksong@yeah.net',       
      url='https://github.com/blacksong',
      classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
)   
