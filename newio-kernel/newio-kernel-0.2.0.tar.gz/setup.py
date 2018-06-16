# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['newio_kernel', 'newio_kernel.monitor']

package_data = \
{'': ['*']}

install_requires = \
['newio>=0.2.0.0,<0.3.0.0',
 'pyllist>=0.3.0.0,<0.4.0.0',
 'terminaltables>=3.1.0.0,<4.0.0.0']

setup_kwargs = {
    'name': 'newio-kernel',
    'version': '0.2.0',
    'description': 'Newio Kernel',
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
