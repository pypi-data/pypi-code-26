# -*- coding: utf-8 -*-
"""
Created on Thu May  3 16:50:29 2018

@author: yili.peng
"""

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='RNWS'
      ,version='0.0.9'
      ,description='read n write stock data'
      ,long_description=readme()
      ,keywords='i/o quant'
      ,author='Yili Peng'
      ,author_email='yili.peng@outlook.com'
      ,packages=['RNWS']
      ,package_data={
		'RNWS': ['data/trading_date.csv'],
		}
      ,lisence='MIT'
      ,zip_safe=False)
        