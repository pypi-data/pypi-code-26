#! -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = 'nlp-zero',
    version = '0.1.6',
    keywords = ' '.join(['nlp', 'tokenizer', 'unsupervised', 'parser', '互信息', '新词发现']),
    description = '无监督NLP工具包|unsupervised nlp toolkit',
    long_description = '基于最小熵原理设计的nlp工具包，可以实现新词发现、分词系统、句模版构建等',
    license = 'MIT Licence',
    url = 'https://kexue.fm',
    author = 'bojone',
    author_email = 'bojone@spaces.ac.cn',
    packages=['nlp_zero'],
    package_dir={'nlp_zero':'nlp_zero'},
    package_data={'nlp_zero':['*.*']},
    platforms = 'any',
)
