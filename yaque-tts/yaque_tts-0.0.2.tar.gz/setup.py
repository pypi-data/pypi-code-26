# *_* coding:utf-8 *_*

from setuptools import setup

setup(
    name='yaque_tts',
    version='0.0.2',
    author='yaquepeng',
    author_email='yaquepeng@outlook.com',
    url='http://www.wdiannao.com',
    description=u'一个简单的，仅仅支持中文的tts模块',
    long_description=open('README.rst').read(),
    packages=['yaque_tts'],
    install_requires=['PyAudio'],
    entry_points={
        'console_scripts': [
            'play=yaque_tts:play'
        ]
    },
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2.7'
    ]
)
