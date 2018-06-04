import os
import is_msgs

def get_include():
    return os.path.split(os.path.dirname(is_msgs.__file__))[0]
