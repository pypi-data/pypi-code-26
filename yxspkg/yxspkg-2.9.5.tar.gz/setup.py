#!/usr/bin/env python3
from setuptools import setup  ,find_packages
import yxspkg
install_modules=['pandas','lxml','bs4','requests','tushare','yxspkg_encrypt','yxspkg_tecfile','yxspkg_wget',
'yxspkg_songzgif','tensorflow','torch','keras']

setup(name='yxspkg',   
      version=yxspkg.__version__,    
      description='My pypi module',    
      author='Blacksong',    
      install_requires=install_modules,
      author_email='blacksong@yeah.net',       
      url='https://github.com/blacksong',
      packages=find_packages(), 
      classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
)   