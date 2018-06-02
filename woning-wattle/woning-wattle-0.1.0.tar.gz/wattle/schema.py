import yaml

from wattle.nodes import Nested, ParentReference


class Schema(object):
    def __init__(self, root_obj):
        self.root_obj = Nested(root_obj)

    def read_dict(self, d):
        obj = self.root_obj.load(d)
        self.create_parent_references(obj, self.root_obj, parent=None)
        return obj

    def read(self, input_file):
        with open(input_file, 'r') as f:
            content = yaml.load(f)
        return self.read_dict(content)

    read_yml = read

    def create_parent_references(self, obj, obj_type, parent=None):
        for field_name, field_type in obj_type.get_fields():
            if isinstance(field_type, ParentReference):
                setattr(obj, field_name, parent)
            elif isinstance(obj_type, Nested):
                self.create_parent_references(
                    getattr(obj, field_name),
                    field_type,
                    parent=obj
                )
