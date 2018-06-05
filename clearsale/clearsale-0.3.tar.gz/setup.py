from distutils.core import setup
from setuptools import find_packages

VERSION = __import__("clearsale").__version__

CLASSIFIERS = [
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Topic :: Software Development',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    # 'Programming Language :: Python :: 3',
]

install_requires = [
    'suds==0.4',
    'xmltodict==0.9.2'
]

setup(
    name="clearsale",
    packages=find_packages(exclude=["tests"]),
    description="Python library to use ClearSale Total Anti Fraud",
    version=VERSION,
    author="Mateus Vanzo de Padua",
    author_email="mateuspaduaweb@gmail.com",
    license='MIT License',
    platforms=['OS Independent'],
    url="https://github.com/mateuspadua/clearsale-python",
    keywords=['clearsale', 'antifraude', 'anti', 'fraude', 'python'],
    include_package_data=True,
    install_requires=install_requires,
    classifiers=CLASSIFIERS,
)
