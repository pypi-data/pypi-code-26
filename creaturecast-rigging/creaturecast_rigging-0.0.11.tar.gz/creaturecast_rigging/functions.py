import sys
import py_maya

def create_node(node_type, **kwargs):
    if node_type not in py_maya.__dict__:
        raise Exception('Node type "%s" does not exist' % node_type)
    return py_maya.__dict__[node_type](**kwargs)
