from ._version import version_info, __version__

from .map import *


def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'jupyter_voter',
        'require': 'jupyter_voter/extension'
    }]
