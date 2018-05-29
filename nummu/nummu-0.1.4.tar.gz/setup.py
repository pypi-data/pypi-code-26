# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['nummu']

package_data = \
{'': ['*']}

install_requires = \
['Pillow==5.0.0', 'array2gif>=1.0,<2.0', 'numpngw==0.0.6']

setup_kwargs = {
    'name': 'nummu',
    'version': '0.1.4',
    'description': 'An animated image maker.',
    'long_description': "# nummu (南無)\n\nAn animated image maker.\n\nNOTE: this project in WIP and thus interface might change a lot. Be cautious when using in production.\n\n|Image|Script|\n|-----|------|\n|![helloworld](https://github.com/soasme/nummu/raw/master/examples/helloworld.png)|[examples/helloworld.py](examples/helloworld.py)|\n|![line](https://github.com/soasme/nummu/raw/master/examples/line.gif)|[examples/line.py](examples/line.py)|\n|![rect](https://github.com/soasme/nummu/raw/master/examples/rect.gif)|[examples/rect.py](examples/rect.py)|\n|![bubblesort](https://gist.github.com/soasme/e3f1a210cc7e7750d304cb43b6aaad23/raw/d6e5687ce8492bd5865f4d7f38a5ec421c5d4c1b/bubblesort.png) Bubble Sort<br> ![heapsort](https://gist.github.com/soasme/e3f1a210cc7e7750d304cb43b6aaad23/raw/d6e5687ce8492bd5865f4d7f38a5ec421c5d4c1b/heapsort.png) Heap Sort<br> ![insertionsort](https://gist.github.com/soasme/e3f1a210cc7e7750d304cb43b6aaad23/raw/d6e5687ce8492bd5865f4d7f38a5ec421c5d4c1b/insertionsort.png) Insertion Sort<br> ![mergesort](https://gist.github.com/soasme/e3f1a210cc7e7750d304cb43b6aaad23/raw/d6e5687ce8492bd5865f4d7f38a5ec421c5d4c1b/mergesort.png) Merge Sort<br> ![quicksort](https://gist.github.com/soasme/e3f1a210cc7e7750d304cb43b6aaad23/raw/d6e5687ce8492bd5865f4d7f38a5ec421c5d4c1b/quicksort.png) Merge Sort<br> ![selectionsort](https://gist.github.com/soasme/e3f1a210cc7e7750d304cb43b6aaad23/raw/d6e5687ce8492bd5865f4d7f38a5ec421c5d4c1b/selectionsort.png) Selection Sort |[examples/sort.py](examples/sort.py)|\n\n## Install\n\n```\n$ pip install nummu\n```\n\n## Usage\n\nBy extending Nummu, you might want to implement a class having these methods: `init()`, `update(delta)`, `draw(palette)`. None of them are absolutely required.\n\n    class HelloWorld:\n\n        def init(self):\n            # Do initial work here\n            self.position = 0\n\n        def update(self, delta):\n            # Do some calculation before draw each frame.\n            # The delta is in millisecond unit.\n            #\n            # Don't forget to raise StopIteration somewhere!\n            #\n            self.position += delta\n            if self.position >= 100:\n                raise StopIteration\n\n        def draw(self, pallete):\n            # Pallete is simply a numpy.zeros instance.\n            # Overwrite any pixels as you want.\n            #\n            pallete[:, self.position, :] = 255\n\nBasic usage:\n\n    # import nummu\n    from nummu import Nummu\n\n    # set file size\n    nm = Nummu(100, 100)\n\n    # extend nummu\n    nm.extend(HelloWorld())\n\n    # export to gif\n    nm.export('helloworld.gif', delay=5)\n\n\nCheck the examples in project repo, and hopefully it might intrigue you some!\n\n## Develop\n\n```\n$ poetry develop\n$ poetry run python examples/helloworld.py\n```\n\n## Credit\n\nThanks Pillow, numpy, numpngw and array2gif! Nummu stands on the shoulder of these giants!\n",
    'author': 'Ju Lin',
    'author_email': 'soasme@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
