# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ampdup']

package_data = \
{'': ['*']}

install_requires = \
['curio>=0.9.0,<0.10.0']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.6.0,<0.7.0',
                                                         'asyncio-contextmanager>=1.0,<2.0']}

setup_kwargs = {
    'name': 'ampdup',
    'version': '0.2.2',
    'description': 'A type-hinted async python mpd client library.',
    'long_description': "ampdup\n======\n\nA type-hinted async python mpd client library.\n\n\nSummary\n=======\n\n`ampdup` is an async/await based MPD library. It currently uses `curio` as its\nmeans of establishing connections.\n\nIt is fully type-hinted and MPD responses are typed as well, so it is able to\nplay nicely with `mypy` and autocompletion such as what is provided by `jedi`.\n\nExamples\n========\n\nFirst a basic usage example. `make()` returns a connected client as a context\nmanager that handles disconnection automatically.\n\n```python\nasync def main():\n    async with MPDClient.make('localhost', 6600) as m:\n        await m.play()\n```\n\nThe IdleClient class provides the `idle()` function. Since `ampdup` is\n`async`/`await`-based this loop can easily run concurrently with other\noperations.\n\n```\nasync def observe_state():\n    async with IdleClient.make('localhost', 6600) as i:\n        while True:\n            changed = await i.idle()\n            handle_changes(changed)\n```\n\nTodo\n====\n\n- [ ] Support command lists.\n- [ ] Support connecting through Unix socket.\n- [ ] Support the more obscure MPD features such as partitions.\n",
    'author': 'Tarcisio Eduardo Moreira Crocomo',
    'author_email': 'tarcisio.crocomo+pypi@gmail.com',
    'url': 'https://gitlab.com/tarcisioe/ampdup',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
