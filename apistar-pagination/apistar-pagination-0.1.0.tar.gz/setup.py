# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['apistar_pagination']

package_data = \
{'': ['*']}

install_requires = \
['apistar>=0.5.30,<0.6.0']

setup_kwargs = {
    'name': 'apistar-pagination',
    'version': '0.1.0',
    'description': 'Pagination tools for API Star.',
    'long_description': '# API Star Pagination\n[![Build Status](https://travis-ci.org/PeRDy/apistar-pagination.svg?branch=master)](https://travis-ci.org/PeRDy/apistar-pagination)\n[![codecov](https://codecov.io/gh/PeRDy/apistar-pagination/branch/master/graph/badge.svg)](https://codecov.io/gh/PeRDy/apistar-pagination)\n[![PyPI version](https://badge.fury.io/py/apistar-pagination.svg)](https://badge.fury.io/py/apistar-pagination)\n\n* **Version:** 0.1.0\n* **Status:** Production/Stable\n* **Author:** José Antonio Perdiguero López\n\nPagination tools for API Star.\n\n## Features\n* Page number pagination.\n* Limit-offset pagination.\n\n## Quick start\nInstall API star Pagination:\n\n```bash\npip install apistar-pagination\n```\n\nUse paginated response in your views:\n\n### Page number pagination\n\n```python\nfrom apistar_pagination import PageNumberResponse\n\ndef page_number(page: http.QueryParam, page_size: http.QueryParam) -> typing.List[int]:\n    collection = ...  # Get your whole collection\n\n    return PageNumberResponse(page=page, page_size=page_size, content=collection)\n```\n\n### Limit-offset pagination\n\n```python\nfrom apistar_pagination import LimitOffsetResponse\n\ndef limit_offset(offset: http.QueryParam, limit: http.QueryParam) -> typing.List[int]:\n    collection = ...  # Get your whole collection\n\n    return LimitOffsetResponse(offset=offset, limit=limit, content=collection)\n```\n',
    'author': 'José Antonio Perdiguero López',
    'author_email': 'perdy@perdy.io',
    'url': 'https://github.com/PeRDy/apistar-pagination',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
