# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['heater', 'heater.resources']

package_data = \
{'': ['*']}

install_requires = \
['cycler>=0.10.0.0,<0.11.0.0',
 'matplotlib>=2.2.0.0,<3.0.0.0',
 'numpy>=1.14.0.0,<2.0.0.0',
 'pillow>=5.1.0.0,<6.0.0.0',
 'pyparsing>=2.2.0.0,<3.0.0.0',
 'python-dateutil>=2.2.0.0,<3.0.0.0']

setup_kwargs = {
    'name': 'heater',
    'version': '0.0.1',
    'description': 'heater makes heatmaps.',
    'long_description': '# heater\n\nheater makes heatmaps.  Inspired by heatmappy but more light weight.\n\n## Installation\n\n    pip install heater\n\n## Usage\n\n``` python\nfrom heater import make_heatmap\n\nwith open("background.png") as f:\n  heatmap = make_heatmap(f, [(1, 2), (3, 4)])\n  heatmap.save("output.png")\n```\n\n## License\n\nheater is licensed under Apache 2.0.  Please see\n[LICENSE] for licensing details.\n\n[LICENSE]: https://github.com/Bogdanp/heater/blob/master/LICENSE\n',
    'author': 'Bogdan Popa',
    'author_email': 'popa.bogdanp@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>= 3.5.0.0, < 4.0.0.0',
}


setup(**setup_kwargs)
