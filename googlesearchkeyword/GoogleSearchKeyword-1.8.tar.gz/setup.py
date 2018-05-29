from setuptools import setup, find_packages

setup(
    name='GoogleSearchKeyword',
    version='1.8',
    packages=["GoogleSearchKeyword", "GoogleSearchKeyword.xgoogle"],
    install_requires=['setuptools', 'requests[security]', 'beautifulsoup4']
)