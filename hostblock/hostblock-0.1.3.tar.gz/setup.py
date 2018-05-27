#!/usr/bin/env python3

from setuptools import setup, find_packages
import hostblock

setup(
    name = 'hostblock',
    description = hostblock.__doc__.strip(),
    url = 'https://github.com/nul-one/hostblock',
    download_url = 'https://github.com/nul-one/hostblock/archive/'+hostblock.__version__+'.tar.gz',
    version = hostblock.__version__,
    author = hostblock.__author__,
    author_email = hostblock.__author_email__,
    license = hostblock.__licence__,
        packages = [ 'hostblock' ],
    entry_points={ 
        'console_scripts': [
            'hostblock=hostblock.__main__:main',
        ],
    },
    install_requires = [
    ],
    python_requires=">=3.4.6",
)

