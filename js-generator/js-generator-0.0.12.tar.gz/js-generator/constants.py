import os

SCRIPT_PATH = os.getcwd()
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(ROOT_DIR, 'templates')

STATE = 'state'
REDUCER = 'reducer'
ACTIONS = 'actions'
STATELESS_FUNCTION_COMPONENT = 'sfc'
CONSTRUCTOR_CLASS_COMPONENT = 'ccc'

TYPES = [
    STATE,
    REDUCER,
    ACTIONS,
    STATELESS_FUNCTION_COMPONENT,
    CONSTRUCTOR_CLASS_COMPONENT
]

CLASS_NAME_PLACEHOLDER = '{}'
COMPONENT_NAME_PLACEHOLDER = '{%%}'
HYPHEN_PLACEHOLDER = '[]'
BRACKETS_PLACEHOLDER = '(*)'

COMPONENT_SUFFIX_DICTIONARY = {
    'component': 'Component',
    'page': 'Page'
}

FOLDER_REQUIRED = [
    STATELESS_FUNCTION_COMPONENT,
    CONSTRUCTOR_CLASS_COMPONENT
]

FILENAME_REQUIRED = [
    STATELESS_FUNCTION_COMPONENT,
    CONSTRUCTOR_CLASS_COMPONENT
]

SEPARATOR = "-----------"

MESSAGES = {
    'start_write_file': 'start writing to file {} of type {}',
    'write_file_complete': '{} was successfully written to {}',
    'aborted': 'action aborted',
    'error_creating_file': 'error creating file',
    'error_no_template_found': 'no template found for type - {}',
    'file_created': 'file {} was created successfully',
    'override': 'file already exist, are you sure you want to override ? ( y / n )',
    'title': 'CLI tool for creating js templates.',
    'filename': 'name of the file to create',
    'class_name': 'main class name',
    'error_no_class_name': '--classname was not satisfied',
    'error_no_filename': '--filename was not satisfied',
    'folder_created': 'folder {} was created',
    'folder_exists': 'folder {} already exists',
    'full_state': 'pass 1 to create a folder with {classname}.state.js, {classname}.reducer.js, {classname}.action.js, '
                  'only --classname is required',
    'install_success': 'generator.py was installed successfully'
}
