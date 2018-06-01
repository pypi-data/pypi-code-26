from wattle.nodes import (Value, Nested, String, Float, Integer, Boolean,
                          List, Choice)
from wattle.schema import Schema


def load_schema(root_node):
    return Schema(root_node)
