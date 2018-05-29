from pathlib import Path
from .logger import *
from .cookers import cooker as ck


__all__ = ['_read_data', '_cook_data', '_read_row_labels', '_has_row_labels']


def _read_data(path, sep='\t', dtype=int):
    """ Reads data.

    Note: All data elements are of the same data type.
    :param path: directory or single path or a list of paths
    :param sep: separator
    :param dtype: data type
    :return: iterable rows
    """
    paths = _parse_data_paths(path)
    for row in _read_multi_data_files(paths, sep, dtype):
        yield row


def _parse_data_paths(path):
    """ Parses data paths from parameter: path.

    :param path: directory or single path or a list of paths
    :return: Iterable paths
    """
    if isinstance(path, list):
        paths = path
    else:
        pt = Path(path)
        if not pt.exists():
            raise FileNotFoundError("File or directory does not exist! path = '%s'" % path)
        if pt.is_dir():
            paths = _files_in_directory(pt)
        else:
            paths = [pt]
    return paths


def _files_in_directory(directory):
    return Path(directory).glob('*')


def _read_single_data_file(path, sep='\t', dtype=int):
    logger.info("Reading '%s'" % path)
    with open(path, 'r') as f:
        for line in f.readlines():
            if line[-1] == '\n':
                line = line[0: -1]
            row = line.split(sep)
            yield [dtype(x) for x in row]


def _read_multi_data_files(paths, sep='\t', dtype=int):
    for path in paths:
        if not Path(path).exists():
            raise FileNotFoundError("File not found! path = '%s'" % path)
        for row in _read_single_data_file(path, sep, dtype):
            yield row


def _read_row_labels(path):
    """ Reads row labels.

    Note: row label file has postfix '.rl' and the same file name with data file.
    :param path: data path (directory or single path or a list of paths)
    :return: iterable (row labels)
    """
    paths = _parse_rl_paths(path)
    for row_label in _read_multi_rl_files(paths):
        yield row_label


def _parse_rl_paths(path):
    """ Parses row label file paths.

    :param path: data path (directory or single path or a list of paths)
    :return: row label file path
    """
    if isinstance(path, list):
        paths = path
    else:
        pt = _data_path_to_rl_path(path)
        if not pt.exists():
            raise FileNotFoundError("File or directory does not exist! path = '%s'" % path)
        if pt.is_dir():
            paths = [_data_path_to_rl_path(path) for path in _files_in_directory(pt)]
        else:
            paths = [pt]
    return paths


def _data_path_to_rl_path(path):
    rl_postfix = '.rl'
    p = Path(path)
    return p if p.is_dir() else p.with_name(p.stem + rl_postfix)


def _read_single_rl_file(path):
    logger.info("Reading '%s'" % path)
    with open(path, 'r') as f:
        for line in f.readlines():
            yield line[0: -1] if line[-1] == '\n' else line


def _read_multi_rl_files(paths):
    for path in paths:
        if not Path(path).exists():
            raise FileNotFoundError("File not found! path = '%s'" % path)
        for row_label in _read_single_rl_file(path):
            yield row_label


def _has_row_labels(path):
    paths_rl = _parse_rl_paths(path)
    paths_data = _parse_data_paths(path)
    i = 0
    for path in paths_rl:
        i += 1
    if i == 0:
        return False
    for path in paths_data:
        i -= 1
    if i != 0:
        return False
    return True


def _cook_data(data, cooker, spices=None):
    """ Cooks data.

    :param data: iterable rows
    :param cooker: cooker name
    :param spices: single tuple or a list of tuples
    :return: iterable rows
    """
    logger.info("cooker: %s" % cooker)
    if not spices:
        spices = ()
    if isinstance(spices, list):
        for row, spice in zip(data, spices):
            yield ck.getattr(cooker)(row, *spice)
    elif isinstance(spices, tuple):
        # all cookers use identical spice
        for row in data:
            cooker_output = ck.getattr(cooker)(row, *spices)
            if _is_cooker_valid(cooker_output):
                yield cooker_output
            else:
                raise Exception('Cooker is not valid. cooker = ' % cooker)

    else:
        raise ValueError("'spices' has wrong format!")


def _is_cooker_valid(cooker_output):
    """ Checks validity the output.
    """
    return True if isinstance(cooker_output, list) else False
