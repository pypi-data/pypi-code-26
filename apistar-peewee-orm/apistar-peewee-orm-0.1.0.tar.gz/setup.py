# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['apistar_peewee_orm']

package_data = \
{'': ['*']}

install_requires = \
['apistar>=0.5.30,<0.6.0', 'peewee>=3.5,<4.0']

setup_kwargs = {
    'name': 'apistar-peewee-orm',
    'version': '0.1.0',
    'description': 'Peewee integration for API Star.',
    'long_description': '# API Star Peewee ORM\n[![Build Status](https://travis-ci.org/PeRDy/apistar-peewee-orm.svg?branch=master)](https://travis-ci.org/PeRDy/apistar-peewee-orm)\n[![codecov](https://codecov.io/gh/PeRDy/apistar-peewee-orm/branch/master/graph/badge.svg)](https://codecov.io/gh/PeRDy/apistar-peewee-orm)\n[![PyPI version](https://badge.fury.io/py/apistar-peewee-orm.svg)](https://badge.fury.io/py/apistar-peewee-orm)\n\n* **Version:** 0.1.0\n* **Status:** Production/Stable\n* **Author:** José Antonio Perdiguero López\n\nPeewee integration for API Star.\n\n## Features\nThis library provides event_hooks to handle connections and commit/rollback behavior based on exceptions in your views.\n\n## Quick start\nInstall API Star Peewee ORM:\n\n```bash\npip install apistar-peewee-orm\n```\n',
    'author': 'José Antonio Perdiguero López',
    'author_email': 'perdy@perdy.io',
    'url': 'https://github.com/PeRDy/apistar-peewee-orm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
