# -*- encoding: utf-8 -*-
from .utils import dependencies

__MANDATORY_PACKAGES__ = '''
pyspark>=2.3.0
PyYAML>=3.12
'''

dependencies.verify_packages(__MANDATORY_PACKAGES__)
