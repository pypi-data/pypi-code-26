# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cliar']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cliar',
    'version': '1.2.0',
    'description': 'Create CLIs with classes and type hints.',
    'long_description': ".. image:: https://img.shields.io/pypi/v/cliar.svg\n  :target: https://pypi.org/project/cliar\n.. image:: https://travis-ci.org/moigagoo/cliar.svg?branch=develop\n  :target: https://travis-ci.org/moigagoo/cliar\n.. image:: https://codecov.io/gh/moigagoo/cliar/branch/develop/graph/badge.svg\n  :target: https://codecov.io/gh/moigagoo/cliar\n\n*****\nCliar\n*****\n\nCreate a CLI from a Python class, make it powerful with type hints.\n\n**Cliar** is a Python tool that helps you create commandline interfaces:\n\n.. code-block:: python\n\n    from cliar import Cliar\n\n    class Git(Cliar):\n        '''Git clone created with Cliar'''\n\n        def clone(self, repo, dir='.'):\n            '''Clone a git repo from REPO to DIR.'''\n\n            print(f'Cloning from {repo} to {dir}')\n\n    if __name__ == '__main__':\n        Git().parse()\n\nRun the script:\n\n.. code-block:: bash\n\n    $ python git.py clone http://foo.bar -d baz\n    Cloning from http://foo.bar to baz\n\n\nRequirements\n============\n\nCliar runs with Python 3.6+ on Windows, Linux, and Mac. There are no external dependencies.\n\n\nInstall\n=======\n\nInstall Cliar from `PyPI <https://pypi.org/project/cliar>`__ with pip:\n\n.. code-block:: bash\n\n    $ pip install cliar\n",
    'author': 'Konstantin Molchanov',
    'author_email': 'moigagoo@live.com',
    'url': 'https://moigagoo.github.io/cliar/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
