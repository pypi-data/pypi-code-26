# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cc_core',
 'cc_core.agent',
 'cc_core.agent.connected',
 'cc_core.agent.cwl',
 'cc_core.agent.red',
 'cc_core.commons',
 'cc_core.commons.connectors',
 'cc_core.commons.schemas',
 'cc_core.commons.schemas.engines']

package_data = \
{'': ['*']}

install_requires = \
['flask>=1.0,<2.0',
 'jinja2>=2.10,<3.0',
 'jsonschema>=2.6,<3.0',
 'psutil>=5.4,<6.0',
 'requests>=2.18,<3.0',
 'ruamel.yaml>=0.14,<0.16']

entry_points = \
{'console_scripts': ['ccagent = cc_core.agent.main:main']}

setup_kwargs = {
    'name': 'cc-core',
    'version': '4.0.0',
    'description': 'CC-Core is part of the Curious Containers project. It provides common functionality for other parts of Curious Containers and implements agents to run data-driven experiments defined in RED or CWL format.',
    'long_description': '# CC-Core\n\nCC-Core is part of the Curious Containers project. CC-Core is part of the Curious Containers project. It provides common functionality for other parts of Curious Containers and implements agents to run data-driven experiments defined in RED or CWL format.\n\n## Acknowledgements\n\nThe Curious Containers software is developed at [CBMI](https://cbmi.htw-berlin.de/) (HTW Berlin -\nUniversity of Applied Sciences). The work is supported by the German Ministry of Economic Affairs and Energy (ZIM\nProject BeCRF, Grant number KF3470401BZ4).\n',
    'author': 'Christoph Jansen',
    'author_email': 'Christoph.Jansen@htw-berlin.de',
    'url': 'https://github.com/curious-containers/cc-core',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
