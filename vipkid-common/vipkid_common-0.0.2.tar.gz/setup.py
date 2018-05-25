from distutils.core import setup
from setuptools import setup
from setuptools import *
setup(
    name="vipkid_common",
    version="0.0.2",
    description="vipkid's common module",
    license = "MIT",
    author="zhaomingming",
    author_email="13271929138@163.com",
    url="http://www.zhaomingming.cn",
    py_modules=['vipkid_common'],
    platforms = 'any',
    packages=find_packages(exclude=['source/*','dist/*' 'docs', 'tests*'])
)
