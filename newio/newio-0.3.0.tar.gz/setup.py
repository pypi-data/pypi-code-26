# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['newio', 'newio.channel']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'newio',
    'version': '0.3.0',
    'description': 'Newio',
    'long_description': None,
    'author': 'guyskk',
    'author_email': 'guyskk@qq.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>= 3.6.0.0',
}


setup(**setup_kwargs)
