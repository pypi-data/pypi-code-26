import logging
from pathlib import Path


class Config(object):
    def __init__(self, data_dir: Path, verbose: int = None, quiet: bool = None, out: str = None):
        self._verbose = verbose
        self._quiet = quiet

        self.data_dir = data_dir
        self.out = out

    @property
    def verbosity(self):
        if self._quiet is not None:
            if self._quiet is True:
                return logging.CRITICAL

        if self._verbose == 0:
            return logging.ERROR
        elif self._verbose == 1:
            return logging.INFO
        elif self._verbose >= 2:
            return logging.DEBUG
