"""Utility functions."""


def valid_handle(handle):
    """Return false if the handle is invalid.

    For example if the handle contains a newline.
    """
    if handle.find("\n") != -1:
        return False
    return True
