import yaml
import os


class ContextLoader(yaml.SafeLoader):

    def __init__(self, stream):
        self._root_path = os.path.dirname(stream.name)
        super(ContextLoader, self).__init__(stream)

    def get_reference(self, node):
        """Resolves references to fields defined in another YAML files

        If this function is used as callback constructor for PYYAML, references are resolved recursively.

        It accepts two kind of references:
          * Format 1: [filename]:Fully.qualified.name
          * Format 2: [filename]

        :param node: YAML text node
        :return: Referenced value
        """

        node_string = self.construct_scalar(node)

        tokenized_path = node_string.split(':')
        target_file = tokenized_path.pop(0) + '.yaml'
        filename = os.path.join(os.path.join(self._root_path, target_file))
        filename = os.path.normpath(filename)

        try:
            target_node = tokenized_path.pop(0)
        except IndexError:
            target_node = ''

        with open(filename, 'r') as f:
            included_yaml = yaml.load(f, ContextLoader)
            field_path = target_node.split('.')
            value = ContextLoader.extract_field(included_yaml, field_path)
            return value

    @staticmethod
    def extract_field(nested_dictionary, field_path_list):
        """This will search in nested dictionaries for the final value defined by a list of consecutive keys.

        >>> ContextLoader.extract_field({"a": {"b": {"c": 42}}}, ['a', 'b', 'c'])
        42

        >>> ContextLoader.extract_field({"a": {"b": {"c": 42, "d": 'towel'}}}, ['a', 'b', 'e'])
        Traceback (most recent call last):
        ...
        KeyError: 'e'

        >>> ContextLoader.extract_field({"a": {"b": {"c": 42}}}, ['a', 'b'])
        {'c': 42}

        :param nested_dictionary: Root dictionary
        :param field_path_list: List of keys to search in order of nesting
        :raises KeyError
        :return: Nested value at the end of the field path list
        """
        next_key = field_path_list.pop(0)
        if len(field_path_list) == 0:
            if next_key:
                try:
                    return nested_dictionary[next_key]
                except KeyError:
                    raise

            else:
                return nested_dictionary
        else:
            return ContextLoader.extract_field(nested_dictionary[next_key], field_path_list)


ContextLoader.add_constructor('!get', ContextLoader.get_reference)
