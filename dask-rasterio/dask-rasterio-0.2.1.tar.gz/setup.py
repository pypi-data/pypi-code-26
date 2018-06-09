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
    'version': '0.2.1',
    'description': 'Read and write rasters in parallel using Rasterio and Dask',
    'long_description': "# dask-rasterio\n\n[![Build Status](https://travis-ci.org/dymaxionlabs/dask-rasterio.svg?branch=master)](https://travis-ci.org/dymaxionlabs/dask-rasterio)\n[![codecov](https://codecov.io/gh/dymaxionlabs/dask-rasterio/branch/master/graph/badge.svg)](https://codecov.io/gh/dymaxionlabs/dask-rasterio) [![Join the chat at https://gitter.im/dymaxionlabs/dask-rasterio](https://badges.gitter.im/dymaxionlabs/dask-rasterio.svg)](https://gitter.im/dymaxionlabs/dask-rasterio?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)\n\n`dask-rasterio` provides some methods for reading and writing rasters in\nparallel using [Rasterio](https://github.com/mapbox/rasterio) and\n[Dask](https://dask.pydata.org) arrays.\n\n\n## Usage\n\n#### Read a multiband raster\n\n```python\n>>> from dask_rasterio import read_raster\n\n>>> array = read_raster('tests/data/RGB.byte.tif')\n>>> array\ndask.array<stack, shape=(3, 718, 791), dtype=uint8, chunksize=(1, 3, 791)>\n\n>>> array.mean()\ndask.array<mean_agg-aggregate, shape=(), dtype=float64, chunksize=()>\n>>> array.mean().compute()\n40.858976977533935\n```\n\n#### Read a single band from a raster\n\n```python\n>>> from dask_rasterio import read_raster\n\n>>> array = read_raster('tests/data/RGB.byte.tif', band=3)\n>>> array\ndask.array<raster, shape=(718, 791), dtype=uint8, chunksize=(3, 791)>\n```\n\n#### Write a singleband or multiband raster\n\n```python\n>>> from dask_rasterio import read_raster, write_raster\n\n>>> array = read_raster('tests/data/RGB.byte.tif')\n\n>>> new_array = array & (array > 100)\n>>> new_array\ndask.array<and_, shape=(3, 718, 791), dtype=uint8, chunksize=(1, 3, 791)>\n\n>>> prof = ... # reuse profile from tests/data/RGB.byte.tif...\n>>> write_raster('processed_image.tif', new_array, **prof)\n```\n\n#### Chunk size\n\nBoth `read_raster` and `write_raster` accept a `block_size` argument that\nacts as a multiplier to the block size of rasters. The default value is 1,\nwhich means the dask array chunk size will be the same as the block size of\nthe raster file. You will have to adjust this value depending on the\nspecification of your machine (how much memory do you have, and the block\nsize of the raster).\n\n\n## Install\n\nInstall with pip:\n\n```\npip install dask-rasterio\n```\n\n## Development\n\nThis project is managed by [Poetry](https://github.com/sdispater/poetry).  If\nyou do not have it installed, please refer to \n[Poetry instructions](https://github.com/sdispater/poetry#installation).\n\nNow, clone the repository and run `poetry install`.  This will create a virtual\nenvironment and install all required packages there.\n\nRun `poetry run pytest` to run all tests.\n\nRun `poetry build` to build package on `dist/`.\n\n\n## Issue tracker\n\nPlease report any bugs and enhancement ideas using the GitHub issue tracker:\n\n  https://github.com/dymaxionlabs/dask-rasterio/issues\n\nFeel free to also ask questions on our\n[Gitter channel](https://gitter.im/dymaxionlabs/dask-rasterio), or by email.\n\n\n## Help wanted\n\nAny help in testing, development, documentation and other tasks is highly\nappreciated and useful to the project.\n\nFor more details, see the file [CONTRIBUTING.md](CONTRIBUTING.md).\n\n\n## License\n\nSource code is released under a BSD-2 license.  Please refer to\n[LICENSE.md](LICENSE.md) for more information.\n",
    'author': 'Damián Silvani',
    'author_email': 'munshkr@gmail.com',
    'url': 'https://github.com/dymaxionlabs/dask-rasterio',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3,<4',
}


setup(**setup_kwargs)
