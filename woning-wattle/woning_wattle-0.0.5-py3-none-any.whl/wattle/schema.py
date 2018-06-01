import yaml

from wattle.nodes import Nested


class Schema(object):
    def __init__(self, root_obj):
        self.root_obj = Nested(root_obj)

    def read_dict(self, d):
        return self.root_obj.load(d)

    def read_yml(self, yml_file):
        return self.read(yml_file)

    def read(self, input_file):
        with open(input_file, 'r') as f:
            content = yaml.load(f)
        return self.read_dict(content)
