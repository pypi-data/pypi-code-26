# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dask_rasterio']

package_data = \
{'': ['*']}

install_requires = \
['dask>=0.17.5,<0.18.0', 'rasterio>=1.0b1,<2.0', 'toolz>=0.9.0,<0.10.0']

setup_kwargs = {
    'name': 'dask-rasterio',
    'version': '0.1.0',
    'description': 'Read and write rasters in parallel using Rasterio and Dask',
    'long_description': '# dask-rasterio\n\n`dask-rasterio` provides some methods for reading and writing rasters in\nparallel using [Rasterio](https://github.com/mapbox/rasterio) and\n[Dask](https://dask.pydata.org) arrays.\n\n## Usage\n\n...\n\n## Install\n\nInstall with pip:\n\n```\npip install dask-rasterio\n```\n\n## Development\n\nThis project is managed by [Poetry](https://github.com/sdispater/poetry).  If\nyou do not have it installed, please refer to \n[Poetry instructions](https://github.com/sdispater/poetry#installation).\n\nNow, clone the repository and run `poetry install`.  This will create a virtual\nenvironment and install all required packages there.\n\nRun `poetry run pytest` to run all tests.\n\nRun `poetry build` to build package on `dist/`.\n\n\n## Issue tracker\n\nPlease report any bugs and enhancement ideas using the GitHub issue tracker:\n\n  https://github.com/dymaxionlabs/dask-rasterio/issues\n\nFeel free to also ask questions on our\n[Gitter channel](https://gitter.im/dymaxionlabs/dask-rasterio), or by email.\n\n\n## Help wanted\n\nAny help in testing, development, documentation and other tasks is highly\nappreciated and useful to the project.\n\nFor more details, see the file [CONTRIBUTING.md](CONTRIBUTING.md).\n\n\n## License\n\nSource code is released under a BSD-2 license.  Please refer to\n[LICENSE.md](LICENSE.md) for more information.\n',
    'author': 'Damián Silvani',
    'author_email': 'munshkr@gmail.com',
    'url': 'https://github.com/dymaxionlabs/dask-rasterio',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3,<4',
}


setup(**setup_kwargs)
