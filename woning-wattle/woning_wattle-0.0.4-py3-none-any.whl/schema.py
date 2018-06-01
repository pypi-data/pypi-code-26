import yaml

from wattle.nodes import Nested


class Schema(object):
    def __init__(self, root_obj):
        self.root_obj = Nested(root_obj)

    def read(self, input_file):
        with open(input_file, 'r') as f:
            content = yaml.load(f)
        return self.root_obj.load(content)
