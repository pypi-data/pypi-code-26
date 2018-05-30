# -*- coding: utf-8 -*-
from __future__ import print_function
from setuptools import setup, find_packages
import sys
LONGDOC = """
juba 简介
=========
“巨霸”中文文本处理：
完整文档见 今日头条 AiMath文章《Python第三方库juba中文文本处理详细使用方法》
GitHub: https://github.com/lihanju/juba

功能与特点
=========
-  支持document term matrix(dtm) 文档词汇矩阵,有三种模式：
   - tf_dtm();词频模式；
   - prob_dtm():概率模式；
   - tfidf_dtm():词频逆文档频率模式。
-  支持term document matrix(tdm) 词汇文档矩阵,有三种模式：
   - tf_tdm();词频模式；
   - prob_tdm():概率模式；
   - tfidf_tdm():词频逆文档频率模式。
-  支持文本相似性分析，有四种方法：
   -cosine_sim():余弦相似度；
   -weight_jaccard_sim():权重jaccard相似度；
   -jaccard_sim():jaccard相似度；
   -bm25_sim():bm25相似度。
-  支持词汇关联分析，有两种模式：
   -two_term_assocs(word_one,word_two,tdm='tf_tdm',norm='False'):计算两个词汇的相关系数；
   -find_assocs(word,mu=0,tdm='tf_tdm',norm='False')：找出word的相关系数的绝对值不少于mu的所有词汇。
-  支持中文文字生成器，自动撰写文章：
   -random_text(textlength,firstWord)：以firstWord开始，生成textlength个词汇的文章。
-  MIT 授权协议

使用例子
=========
import jieba
from juba import Similar,Markov

docs = [['通信', '有效'], ['领域', '自然语言', '计算机科学', '自然语言', '理解', '自然语言', '自然语言', '理论'], ['通信', '有效', '理解', '理论'],
       ['领域', '自然语言', '计算机科学', '自然语言', '理解', '自然语言', '自然语言', '理论', '通信', '有效', '理解', '理论'],['我','喜欢','你们'],
        ['我','谢谢','您']]
S=Similar(docs)
S.tf_dtm()
S.tf_tdm()
S.cosine_sim(dtm='tf_dtm')
S.two_term_assocs('有效','理论',tdm='tf_tdm')
S.find_assocs('计算机科学',tdm='tf_tdm',mu=0.7)

text='在全国网络安全和信息化工作会议上，习近平总书记从党长期执政和国家长治久安的高度，深刻阐明了网信事业发展的一系列方向性、全局性、根本性问题，
对加强党对网信工作的领导提出了明确要求，为新时代网络安全和信息化发展提供了根本遵循。坚持正确政治方向，就要以习近平新时代中国特色社会主义思想为指导，
把网络强国战略思想贯穿到网信工作各方面、诸环节。党的十八大以来，我们之所以能推动网信事业取得历史性成就，最根本的就在于有以习近平同志为核心的党中央的坚强领导，
有网络强国战略思想的正确引领。'
text=list(jieba.cut(text))#使用jieba对文本进行分词
M=Markov(text)
M.random_text(200,"我")

安装说明
==========
代码对 Python 2/3 均兼容
-  全自动安装：pip install juba
-  手动安装：将 juba 目录放置于当前目录或者 site-packages 目录
-  通过 ``import juba`` 来引用

"""
setup(
    name="juba",
    version="0.1.2",
    author="Li Hanju",
    author_email="99959828@qq.com",
    description="A Python library for Chinese text analysis.",
    long_description=LONGDOC,
    url='https://github.com/lihanju/juba',
    packages=find_packages(),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Indexing',
        'Topic :: Text Processing :: Linguistic',
    ],
    zip_safe=True,
)