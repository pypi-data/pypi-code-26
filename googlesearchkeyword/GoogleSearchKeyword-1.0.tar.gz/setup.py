from setuptools import setup, find_packages

setup(
    name='GoogleSearchKeyword',
    version='1.0',
    packages=find_packages(exclude=['tests']),
    install_requires=['setuptools', 'requests[security]', 'beautifulsoup4']
)