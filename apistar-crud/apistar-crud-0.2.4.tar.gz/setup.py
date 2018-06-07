# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['apistar_crud']

package_data = \
{'': ['*']}

install_requires = \
['apistar>=0.5.30,<0.6.0']

setup_kwargs = {
    'name': 'apistar-crud',
    'version': '0.2.4',
    'description': 'API Star tools to create CRUD resources.',
    'long_description': 'API Star CRUD\n=============\n|build-status| |coverage| |version|\n\n:Version: 0.2.4\n:Status: Production/Stable\n:Author: José Antonio Perdiguero López\n\nAPI Star tools to create CRUD resources.\n\nFeatures\n--------\nThe resources are classes with a default implementation for **methods**:\n\n* `create`: Create a new element for this resource.\n* `retrieve`: Retrieve an element of this resource.\n* `update`: Update (partially or fully) an element of this resource.\n* `delete`: Delete an element of this resource.\n* `list`: List resource collection.\n* `drop`: Drop resource collection.\n\n----\n\nThe **routes** for these methods are:\n\n======== ====== ==============\nMethod   Verb   URL\n======== ====== ==============\ncreate   POST   /\nretrieve GET    /{element_id}/\nupdate   PUT    /{element_id}/\ndelete   DELETE /{element_id}/\nlist     GET    /\ndrop     DELETE /\n======== ====== ==============\n\nQuick start\n-----------\nInstall API star CRUD:\n\n.. code:: bash\n\n    pip install apistar-crud\n\nCreate a **model** for your resource:\n\n.. code:: python\n\n    # Example using SQL Alchemy\n\n    class PuppyModel(Base):\n        __tablename__ = "Puppy"\n\n        id = Column(Integer, primary_key=True)\n        name = Column(String)\n\nCreate an **input type** and **output_type** for your resource:\n\n.. code:: python\n\n    class PuppyInputType(types.Type):\n        name = validators.String()\n\n    class PuppyOutputType(types.Type):\n        id = validators.Integer()\n        name = validators.String()\n\nNow create your **resource**:\n\n.. code:: python\n\n    from apistar_crud.sqlalchemy import Resource\n\n    class PuppyResource(metaclass=Resource):\n        model = PuppyModel\n        input_type = PuppyInputType\n        output_type = PuppyOutputType\n        methods = ("create", "retrieve", "update", "delete", "list", "drop")\n\nThe resource generates his own **routes**, so you can add it to your main routes list:\n\n.. code:: python\n\n    from apistar import Include\n\n    routes = [\n        Include("/puppy", "Puppy", PuppyResource.routes),\n    ]\n\n\n.. |build-status| image:: https://travis-ci.org/PeRDy/apistar-crud.svg?branch=master\n    :alt: build status\n    :scale: 100%\n    :target: https://travis-ci.org/PeRDy/apistar-crud\n.. |coverage| image:: https://codecov.io/gh/PeRDy/apistar-crud/branch/master/graph/badge.svg\n    :alt: coverage\n    :scale: 100%\n    :target: https://codecov.io/gh/PeRDy/apistar-crud/branch/master/graph/badge.svg\n.. |version| image:: https://badge.fury.io/py/apistar-crud.svg\n    :alt: version\n    :scale: 100%\n    :target: https://badge.fury.io/py/apistar-crud\n',
    'author': 'José Antonio Perdiguero López',
    'author_email': 'perdy@perdy.io',
    'url': 'https://github.com/PeRDy/apistar-crud',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
