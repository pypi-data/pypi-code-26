# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cc_faice',
 'cc_faice.agent',
 'cc_faice.agent.cwl',
 'cc_faice.agent.red',
 'cc_faice.commons',
 'cc_faice.export',
 'cc_faice.file_server',
 'cc_faice.schema',
 'cc_faice.schema.list',
 'cc_faice.schema.show',
 'cc_faice.schema.validate']

package_data = \
{'': ['*']}

install_requires = \
['cc-core>=4.0,<4.1',
 'docker>=3.2,<4.0',
 'flask>=1.0,<2.0',
 'jsonschema>=2.6,<3.0']

entry_points = \
{'console_scripts': ['faice = cc_faice.main:main']}

setup_kwargs = {
    'name': 'cc-faice',
    'version': '4.0.1',
    'description': 'FAICE (Fair Collaboration and Experiments) is part of the Curious Containers project and enables researchers to perform and distribute reproducible data-driven experiments defined in RED or CWL format.',
    'long_description': '# FAICE\n\nFAICE (Fair Collaboration and Experiments) is part of the Curious Containers project and enables researchers to perform\nand distribute reproducible data-driven experiments defined in RED or CWL format.\n\n## Acknowledgements\n\nThe Curious Containers software is developed at [CBMI](https://cbmi.htw-berlin.de/) (HTW Berlin -\nUniversity of Applied Sciences). The work is supported by the German Ministry of Economic Affairs and Energy (ZIM\nProject BeCRF, Grant number KF3470401BZ4).\n',
    'author': 'Christoph Jansen',
    'author_email': 'Christoph.Jansen@htw-berlin.de',
    'url': 'https://curious-containers.github.io/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
