import os
from bfutils import constants
from bfutils import file

# Read the config file
import yaml
with open( constants.CONFIG_YAML, 'r' ) as f:
    constants.CONFIG = yaml.safe_load( f )
del yaml

