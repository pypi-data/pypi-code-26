# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['nummu']

package_data = \
{'': ['*']}

install_requires = \
['numpngw']

setup_kwargs = {
    'name': 'nummu',
    'version': '0.1.2',
    'description': 'An animated image maker.',
    'long_description': "# nummu (南無)\n\nAn animated image maker.\n\nNOTE: this project in WIP and thus interface might change a lot. Be cautious when using in production.\n\n## Usage\n\nBy extending Nummu, you might want to implement a class having these methods: `init()`, `update(delta)`, `draw(palette)`. None of them are absolutely required.\n\n    class HelloWorld:\n\n        def init(self):\n            # Do initial work here\n            self.position = 0\n\n        def update(self, delta):\n            # Do some calculation before draw each frame.\n            # The delta is in millisecond unit.\n            #\n            # Don't forget to raise StopIteration somewhere!\n            #\n            self.position += delta\n            if self.position >= 100:\n                raise StopIteration\n\n        def draw(self, pallete):\n            # Pallete is simply a numpy.zeros instance.\n            # Overwrite any pixels as you want.\n            #\n            pallete[:, self.position, :] = 255\n\nBasic usage:\n\n    # import nummu\n    from nummu import Nummu\n\n    # set file size\n    nm = Nummu(100, 100)\n\n    # extend nummu\n    nm.extend(HelloWorld())\n\n    # export to apng\n    nm.export('helloworld.png', delay=5)\n\n![helloworld](https://github.com/soasme/nummu/raw/master/examples/helloworld.png)\n\nCheck the examples in project repo, and hopefully it might intrigue you some!\n\n## Credit\n\nThanks numpy and numpngw! Nummu stands on the shoulder of these giants!\n",
    'author': 'Ju Lin',
    'author_email': 'soasme@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>= 3.6.0.0, < 4.0.0.0',
}


setup(**setup_kwargs)
