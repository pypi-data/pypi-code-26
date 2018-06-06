"""Simple file system utils."""
import os


def makedirs(path, is_file, to_abs=False):
    """Make directory from path (filename or directory) if it doesn't already exist.

    Args:
        path (str): Absolute path of directory or filename.
        is_file (bool): Whether the path is a directory of filename.
            If True, then path is treated as a filename and its parent directory is created.
            If False, then path is treated as a directory and it is created.
        to_abs (bool): If True, convert the path to absolute path.
            If False, assume that the path is absolute. Default False.

    Returns:
        None
    """
    if to_abs:
        if not os.path.isabs(path):
            path = os.path.abspath(path)

    if not os.path.isabs(path):
        raise ValueError("Path must be an absolute path. This method does not deal with relative paths. "
                         "Use `to_abs` if you want to explicitly convert path to absolute.")

    if is_file:
        directory = os.path.dirname(path)
    else:
        directory = path

    # If directory does not exist, then simple create it.
    if not os.path.exists(directory):
        os.makedirs(directory)

    # elif the directory exists
    else:
        # Assert that the path is a directory
        if not os.path.isdir(directory):
            raise OSError("Path already exists but is not a directory! Path: {}".format(directory))
        else:
            # Alles in Ordnung
            pass

    return
