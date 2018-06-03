import gzip
import itertools
import logging
import os
import pickle
import sys
from pathlib import Path


class DataSet:
    """Represents collections of local WHDLoad Slave files and
    WHDLoad Install Packages from the WHDLoad website (www.whdload.de).
    """

    DATA_DIR = ".igamelister"

    logger = logging.getLogger(__name__)

    def __init__(self, config) -> None:
        """Initialize a new instance of the Data class.
        """
        DataSet.logger = logging.getLogger(__name__)
        self._config = config
        self.data = []
        self.next_id = itertools.count()

    def _load_data(self, file_name: str) -> list:

        def is_non_zero_file(x):
            return os.path.isfile(x) and os.path.getsize(x) > 0

        data_dir = self._config.obj.data_dir
        data_file = Path(os.path.join(data_dir, file_name))
        if is_non_zero_file(data_file):
            with gzip.open(data_file, "rb") as fp:
                try:
                    return pickle.load(fp)
                except (IOError, EOFError, OSError, pickle.UnpicklingError):
                    DataSet.logger.exception(f"Problem reading data file '{data_file}'. Exiting.")
                    sys.exit(1)
        else:
            if os.path.isfile(data_file):
                data_file.unlink()
                raise ValueError(f"Data file '{file_name}' is zero bytes.  Deleted file.")
            else:
                raise ValueError(f"Data file '{file_name}' not found.")

    def _save_data(self, file_name: str, source: list):
        data_dir = self._config.obj.data_dir
        data_file = Path(os.path.join(data_dir, file_name))
        with gzip.open(data_file, "wb") as fp:
            pickle.dump(source, fp)
