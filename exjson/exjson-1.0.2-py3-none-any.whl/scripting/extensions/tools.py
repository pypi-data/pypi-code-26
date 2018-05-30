import os


def get_null_value(value):
    """Gets None from null token"""
    if value.lower().strip(' ') == "null":
        return None
    else:
        return value

def is_windows():
    """Determines if the current operating system is a windows system"""
    return os.name == "nt"

