import yaml

__all__ = ['dump', 'load']


class Dumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(Dumper, self).increase_indent(flow, False)


def represent_dict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)


yaml.add_representer(dict, represent_dict)


def _insert_newline(line):
    if line.startswith('  - '):
        return '\n' + line
    return line


def _format_mapping_newlines(section):
    lines = section.splitlines()

    # skip section header + first subsection line
    lines = lines[:2] + [_insert_newline(line) for line in lines[2:]]
    return '\n'.join(lines)


def _dump(data):
    output = yaml.dump(data, Dumper=Dumper, default_flow_style=False)
    output = _format_mapping_newlines(output)
    return output


def dump(data):
    """Custom PyYAML dump command to get the approximately desired formatting.

    - ``Dumper`` ensures that lists/maps properly indent.
    - ``represent_dict`` disables map sorting by key name.
    - ``default_flow_style`` turns off inlined maps when nesting.
    - Newlines are also inserted between sections/subsectinons.
    """
    data = data.copy()

    # Add spacing between sections
    sections = [data]
    if 'packages' in data:
        sections.append({'packages': data.pop('packages')})
    if 'dependencies' in data:
        sections.append({'dependencies': data.pop('dependencies')})

    return '\n\n'.join([_dump(section) for section in sections])


load = yaml.load
