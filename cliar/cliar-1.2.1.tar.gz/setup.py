# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cliar']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cliar',
    'version': '1.2.1',
    'description': 'Create CLIs with classes and type hints.',
    'long_description': "[![image](https://img.shields.io/pypi/v/cliar.svg)](https://pypi.org/project/cliar)\n[![image](https://travis-ci.org/moigagoo/cliar.svg?branch=develop)](https://travis-ci.org/moigagoo/cliar)\n[![image](https://codecov.io/gh/moigagoo/cliar/branch/develop/graph/badge.svg)](https://codecov.io/gh/moigagoo/cliar)\n\n# Cliar\n\nCliar is yet another Python package to create commandline interfaces. It focuses on simplicity, extensibility, and testability:\n\n-   Creating a CLI is as simple as creating subclassing `cliar.Cliar`.\n-   Extending a CLI is as simple as subclassing from the base CLI class.\n-   Testing a CLI is as simple as unittesting a class.\n\nCliar's mission is to let the programmer focus on the business logic instead of building an interface for it. At the same time, Cliar doesn't want to stand in the programmer's way, so it provides means to customize the generated CLI.\n\n# Installation\n\n```shell\npip install cliar\n```\n\nCliar runs with Python 3.6+ on Windows, Linux, and Mac. There are no dependencies outside Python's standard library.\n\n# Basic Usage\n\nLet's create a calculator app. Version 1.0.0 will implement only addition of two real numbers.\n\nHere's how you do it with Cliar:\n\n```python\nfrom cliar import Cliar\n\n\nclass Calculator(Cliar):\n    '''Calculator app.'''\n\n    def add(self, x: float, y: float):\n        '''Add two real numbers.'''\n\n        print(f'The sum of {x} and {y} is {x+y}.')\n\n\nif __name__ == '__main__':\n    Calculator().parse()\n```\n\nSave this code as `calc.py` and run it with different inputs:\n\n```shell\n$ python run calc.py add 12 34\nThe sum of 12.0 and 34.0 is 46.0.\n\n$ python run calc.py foo bar\nusage: calc.py add [-h] x y\ncalc.py add: error: argument x: invalid float value: 'foo'\n\n$ python run calc.py -h\nusage: calc.py [-h] {add} ...\n\nCalculator app.\n\noptional arguments:\n  -h, --help  show this help message and exit\n\ncommands:\n  {add}       Available commands:\n    add       Add two real numbers.\n\n$ python calc.py add -h\nusage: calc.py add [-h] x y\n\nAdd two real numbers.\n\npositional arguments:\n  x\n  y\n\noptional arguments:\n  -h, --help  show this help message and exit\n```\n\nThere are a few things to note in the code above:\n\n-   It's a regular Python class with a regular Python method. You don't need to learn any new syntax to use Cliar.\n-   The `add` method was converted into `add` command, and its positional params were converted into positional commandline args.\n-   We don't convert `x` or `y` to `float` or handle any potential conversion errors in the `add` body. Instead, we treat `x` and `y` as if they were already guaranteed to be floats. That's because Cliar does the validation and conversion for us, using the information from `add`'s type hints. Note how invalid input doesn't even reach your code.\n-   The `--help` and `-h` flags are added automatically and the help messages were generated from the docstrings.\n",
    'author': 'Konstantin Molchanov',
    'author_email': 'moigagoo@live.com',
    'url': 'https://moigagoo.github.io/cliar/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
