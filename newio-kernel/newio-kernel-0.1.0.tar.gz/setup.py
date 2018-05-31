# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['newio_kernel']

package_data = \
{'': ['*']}

install_requires = \
['llist>=0.5.0.0,<0.6.0.0',
 'newio>=0.1.0.0,<0.2.0.0',
 'pytest-cov>=2.5.0.0,<3.0.0.0']

setup_kwargs = {
    'name': 'newio-kernel',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'guyskk',
    'author_email': 'guyskk@qq.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>= 3.6.0.0',
}


setup(**setup_kwargs)
