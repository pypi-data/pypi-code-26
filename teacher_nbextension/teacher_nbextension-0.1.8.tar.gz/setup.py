# from nbsetuptools import setup
import setuptools
from setuptools import setup
from os.path import abspath, dirname, join

NAME = 'teacher_nbextension'
AUTHOR = 'ibelyalov'
EMAIL = 'ibelyalov@yandex.ru'
DESCRIPTION = 'Teacher extension for Jupyter'
URL = 'http://github.com/theotheo/teacher_nbextension'

setup(
    name=NAME,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    version="0.1.8",
    static=join(abspath(dirname(__file__)), 'static'),
    install_requires=[
        'python-logstash'
    ],
    packages=setuptools.find_packages(),
    include_package_data=True
)
