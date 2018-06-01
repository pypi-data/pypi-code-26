import empy, copy
from kooki.tools import get_front_matter
from collections import OrderedDict
from kooki.common import Metadata
from kooki.exception import BadMetadata
import pretty_output


def apply_template(data, metadata):

    result = None

    if isinstance(data, list):
        result = []
        for file_content in data:
            front_matter, content = get_front_matter(file_content)
            unique_metadata = get_metadata(front_matter, metadata)
            result.append(apply_interpreter(content, unique_metadata))

    elif isinstance(data, OrderedDict):
        result = OrderedDict()
        for file_path, file_content in data.items():
            front_matter, content = get_front_matter(file_content)
            unique_metadata = get_metadata(front_matter, metadata)
            result[file_path] = apply_interpreter(content, unique_metadata)

    elif isinstance(data, dict):
        result = {}
        for file_path, file_content in data.items():
            front_matter, content = get_front_matter(file_content)
            unique_metadata = get_metadata(front_matter, metadata)
            result[file_path] = apply_interpreter(content, unique_metadata)

    elif isinstance(data, str):
        result = ''
        front_matter, content = get_front_matter(data)
        unique_metadata = get_metadata(front_matter, metadata)
        result = apply_interpreter(content, unique_metadata)

    else:
        raise Exception('templating bad data type {}'.format(type(data)))

    return result


def get_metadata(front_matter, metadata):
    metadata_copy = Metadata()
    metadata_copy.update(front_matter)
    metadata_copy.update(metadata)
    return metadata_copy


def apply_interpreter(content, metadata):
    interpreter = empy.Interpreter()
    interpreter.setPrefix('@')
    result = interpreter.expand(content, metadata)
    return result


def check_template(data, metadata):
    pretty_output.title_3('calls')
    if isinstance(data, list):
        for file_content in data:
            front_matter, content = get_front_matter(file_content)
            unique_metadata = get_metadata(front_matter, metadata)
            check_template_interpreter('', content, unique_metadata)

    elif isinstance(data, OrderedDict):
        for file_path, file_content in data.items():
            front_matter, content = get_front_matter(file_content)
            unique_metadata = get_metadata(front_matter, metadata)
            check_template_interpreter(file_path, content, unique_metadata)

    elif isinstance(data, dict):
        for file_path, file_content in data.items():
            front_matter, content = get_front_matter(file_content)
            unique_metadata = get_metadata(front_matter, metadata)
            check_template_interpreter(file_path, content, unique_metadata)

    elif isinstance(data, str):
        front_matter, content = get_front_matter(data)
        unique_metadata = get_metadata(front_matter, metadata)
        check_template_interpreter('', content, unique_metadata)


values = []

def before_evaluate(expression, locals):
    global values
    found = True
    value = ''
    try:
        value = eval(expression, locals)
    except:
        found = False
    values.append((expression, found, value))


def check_template_interpreter(file_name, content, metadata):
    try:
        global values
        interpreter = empy.Interpreter()
        interpreter.setPrefix('@')

        hook = empy.Hook()
        hook.beforeEvaluate = before_evaluate
        interpreter.register(hook)

        interpreter.expand(content, metadata)
    except Exception as e:
        print(e)
        raise BadMetadata()
    finally:
        output = []
        pretty_output.info(file_name)
        for value in values:
            name = value[0]
            if value[1]:
                output.append({'name': name, 'status': '[ok]'})
            else:
                output.append({'name': name, 'status': ('[error]', 'red')})
        pretty_output.infos(output, [('name', 'blue'), ('status', 'green')])
