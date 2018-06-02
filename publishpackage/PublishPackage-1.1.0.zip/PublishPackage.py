#coding:utf-8

import os

os.system('pip install twine')
os.system('python setup.py sdist')
os.system('python setup.py install')
os.system('twine upload dist/*')

'''
from distutils.core import setup

setup(
    name = 'Headers',      
    version = '1.1.0',
    py_modules = ['Headers'],
    author = 'Chirco',        
    author_email = '503588699@qq.com',
    description = '解析浏览器headers为字典类型'   
    )

'''
