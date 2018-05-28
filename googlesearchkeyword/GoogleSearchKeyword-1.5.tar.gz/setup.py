from setuptools import setup, find_packages

setup(
    name='GoogleSearchKeyword',
    version='1.5',
    packages=["GoogleSearchKeyword"],
    install_requires=['setuptools', 'requests[security]', 'beautifulsoup4']
)