# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import codecs
import os
import bbindex

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

long_desc = """

BBIndex
===============

The World ’ s First Well Diversified Crypto Asset Indices. 

Index Description
--------------

B7:
The B7 (BlockChain Top 7 Index) select the top 7 cryptocurrency ranked by the 30-day average market-cap. This is the mega investment in cryptocurrency market.

B20:
The B20 (BlockChain Top 20 Index ) select the top 20 cryptocurrency ranked by the 30-day average market-cap. This portfolio represents the large-cap investment in cryptocurrency market.

BT7:
The BT7 (BlockChain Tokens Top 7 Index) select the top 7 tokens in cryptocurrency market ranked by the 30-day average market-cap. This portfolio invest in the first tier tokens.

BT30:
The BT30 (BlockChain Tokens Top 30 Index) select the top 30 tokens in cryptocurrency market ranked by the 30-day average market-cap. This portfolio invest in the first tier and the second tier tokens.

B50:
The B50 (BlockChain Top 50 Index ) select the top 50 cryptocurrency ranked by the 30-day average market-cap. This portfolio represent the large-cap and mid-cap investment in cryptocurrency market.

B20XX:
The B20XX (BlockChain Top 20 ex Top 7 Index ) select the top 20 cryptocurrency ranked by the 30-day average market-cap and exclude B7 from it. This portfolio remove B7 from the large-cap investment in cryptocurrency market.
B50XX:

The B50XX (BlockChain Top 50 Top 20 Index ) select the top 50 cryptocurrency ranked by the 30-day average market-cap and exclude B20 from it. This portfolio represent the mid-cap investment in cryptocurrency market.

B7X:
The B7X (BlockChain Top 7 ex Bitcoin Index ) select the top 7 cryptocurrency ranked by the 30-day average market-cap and exclude Bitcoin from it. This portfolio removes the Bitcoin from the mega investment.

B20X:
The B20X (BlockChain Top 20 ex Bitcoin Index ) select the top 20 cryptocurrency ranked by the 30-day average market-cap and exclude Bitcoin from it. This portfolio represents the large-cap investment except Bitcoin in cryptocurrency market.

B50X:
The B50X (BlockChain Top 50 ex Bitcoin Index ) select the top 50 cryptocurrency ranked by the 30-day average market-cap and exclude Bitcoin from it. This portfolio represent the large-cap and mid-cap investment in cryptocurrency market except Bitcoin.

BI7:
The BP7 (BlockChain Platform Top 7 Index) select the top 7 platform coins in cryptocurrency market ranked by the 30-day average market-cap. This portfolio invest in the first tier platform coins.

BC7:
The BC7 (BlockChain Currency Top 7 Index) select the top 7 digital currency in cryptocurrency market ranked by the 30-day average market-cap. This portfolio invest in the first tier digital currency.

BI20:
The BP20 (BlockChain Platform Top 20 Index) select the top 20 platform coins in cryptocurrency market ranked by the 30-day average market-cap. This portfolio invest in the first tier and the second tier platform coins.

BI20XX:
The BP20XX(BlockChain Platform Top 20 ex Top 7 Index) select the top 20 platform coins and exclude BP7 from it. This portfolio invest in the second tier platform coins.

BC20:
The BC20 (BlockChain Currency Top 20 Index) select the top 20 digital currency in cryptocurrency market ranked by the 30-day average market-cap. This portfolio invest in the first tier and the second tier digital currency.

BC20XX:
The BC20XX(BlockChain Currency Top 20 ex Top 7 Index) select the top 20 digital currency and exclude BC7 from it. This portfolio invest in the second tier digital currency.

BT30XX:
The BT30XX(BlockChain Tokens Top 30 ex Top 7 Index) select the top 30 tokens and exclude BT7 from it. This portfolio invest in the second tier tokens.

B20C:
The B20C(BlockChain Top 20 Currency Index) select the digital currency in top 20 cryptocurrency ranked by the 30-day average market-cap. This portfolio invest in the large cap digital currency.

B20T:
The B20T(BlockChain Top 20 Token Index) select the tokens in top 20 cryptocurrency ranked by the 30-day average market-cap. This portfolio invest in the large cap tokens.

B20I:
The B20P(BlockChain Top 20 Platform Index) select the platform coins in top 20 cryptocurrency ranked by the 30-day average market-cap. This portfolio invest in the large cap platform coins.

B50C:
The B50C(BlockChain Top 50 Currency Index) select the digital currency in top 50 cryptocurrency ranked by the 30-day average market-cap. This portfolio invest in the large-cap and mid-cap digital currency.

B50T:
The B50T(BlockChain Top 50 Token Index) select the tokens in top 50 cryptocurrency ranked by the 30-day average market-cap. This portfolio invest in the large-cap and mid-cap tokens.

B50I:
The B50P(BlockChain Top 50 Platform Index) select the platform coins in top 50 cryptocurrency ranked by the 30-day average market-cap. This portfolio invest in the large-cap and mid-cap platform coins.

B50XXC:
The B50XXC(BlockChain Top 50 ex top 20 Currency Index) select the digital currency in top 50 cryptocurrency ranked by the 30-day average market-cap and exclude B20C from it. This portfolio invest in the mid-cap digital currency.

B50XXT:
The B50XXT(BlockChain Top 50 ex top 20 Token Index) select the tokens in top 50 cryptocurrency ranked by the 30-day average market-cap and exclude B20T from it. This portfolio invest in the mid-cap tokens.

B50XXI:
The B50XXP(BlockChain Top 50 ex top 20 Platform Index) select the platform coins in top 50 cryptocurrency ranked by the 30-day average market-cap and exclude B20P from it. This portfolio invest in the mid-cap platform coins.


Install
--------------

    pip install bbindex
    
Upgrade
---------------

    pip install bbindex --upgrade
    
    
"""


setup(
    name='bbindex',
    version=bbindex.__version__,
    description='The World\'s First Well Diversified Crypto Asset Indices',
#     long_description=read("READM.rst"),
    long_description = long_desc,
    author='tushare.org',
    author_email='waditu@163.com',
    license='Apache 2.0',
    url='http://tushare.org',
    keywords='Crypto Asset Index',
    classifiers=['Development Status :: 4 - Beta',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'License :: OSI Approved :: BSD License'],
    packages=find_packages(),
    package_data={'': ['*.csv']},
)