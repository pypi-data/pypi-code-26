from setuptools import setup

# Runtime dependencies. See requirements.txt for development dependencies.
dependencies = [
    'requests',
]

version = '1.0.2.3'

setup(name='okexfix',
    version=version,
    description = 'Python client for the okexfix API. A copy of (https://github.com/haobtc/okexfix)',
    author = 'beshrek',
    author_email = 'pbc.cmbc@qq.com',
    url = 'https://github.com/beshrek/okexfix',
    license = 'MIT',
    packages=['okexfix'],
    install_requires = dependencies,
    keywords = ['bitcoin', 'btc'],
    classifiers = [],
    zip_safe=True)
