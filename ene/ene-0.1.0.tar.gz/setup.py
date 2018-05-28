# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ene']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=18.0.0.0', 'click>=6.0.0.0']

setup_kwargs = {
    'name': 'ene',
    'version': '0.1.0',
    'description': 'Automatically track and sync anime watching progress',
    'long_description': '# ENE\n',
    'author': 'Peijun Ma',
    'author_email': 'peijun.ma@protonmail.com',
    'url': 'https://github.com/MaT1g3R/ene',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>= 3.6.0.0',
}


setup(**setup_kwargs)
