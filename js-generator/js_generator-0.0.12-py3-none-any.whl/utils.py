import os
import sys
from constants import CLASS_NAME_PLACEHOLDER, MESSAGES, \
    SCRIPT_PATH, TEMPLATES_DIR, HYPHEN_PLACEHOLDER, SEPARATOR, FOLDER_REQUIRED, REDUCER, STATE, ACTIONS, \
    BRACKETS_PLACEHOLDER, COMPONENT_SUFFIX_DICTIONARY, COMPONENT_NAME_PLACEHOLDER


class Utils:
    def __init__(self):
        pass

    def create(self, args):
        if args.type in FOLDER_REQUIRED or args.full_state:
            folder_path = self.create_folder(args.classname)
            if args.full_state:
                self.create_full_state(folder_path, args.classname)
            else:
                created_file = self.create_file(os.path.join(folder_path, args.filename))
                self.write_to_file(created_file, args.type, args.classname, filename=args.filename)
                self.create_file(os.path.join(folder_path, self.get_css_filename(args.filename)))

        else:
            created_file = self.create_file(self.get_full_path(args.filename))
            self.write_to_file(created_file, args.type, args.classname)

    def create_folder(self, class_name):
        full_path = self.get_full_path(class_name)
        os.makedirs(full_path)
        self.log('[create_folder]', MESSAGES.get('folder_created').format(class_name))
        return full_path

    def create_full_state(self, folder_path, class_name):
        self.create_full_state_file(folder_path, REDUCER, class_name)
        self.create_full_state_file(folder_path, STATE, class_name)
        self.create_full_state_file(folder_path, ACTIONS, class_name)

    def create_full_state_file(self, folder_path, file_type, class_name):
        full_path = self.get_state_path(folder_path, class_name, file_type)
        created_file = self.create_file(full_path)
        self.write_to_file(created_file, file_type, class_name)

    def create_file(self, filename):
        try:
            created_file = open(filename, 'w')
            self.log('[create_file]', MESSAGES.get('file_created').format(filename))
            return created_file
        except IOError:
            self.log('[create_file]', MESSAGES.get('error_creating_file').format(filename))
            self.abort()

    def write_to_file(self, created_file, file_type, class_name, filename=''):
        self.log('[write_to_file]', MESSAGES['start_write_file'].format(created_file.name, file_type))
        updated_file = self.inject_template_variables(file_type, class_name, filename)
        created_file.write(updated_file)
        self.log('[write_to_file]', MESSAGES['write_file_complete'].format(file_type, created_file.name))

    def inject_template_variables(self, file_type, class_name, filename):
        camel_cased_class_name = self.get_camel_case_string(class_name)
        template_content = self.get_template_content(file_type)
        camel_cased = self.replace_placeholder(template_content, camel_cased_class_name, CLASS_NAME_PLACEHOLDER)
        brackets = self.replace_placeholder(camel_cased, self.get_css_filename(filename), BRACKETS_PLACEHOLDER)
        components_suffix = self.replace_placeholder(
            brackets,
            self.get_component_suffix(filename),
            COMPONENT_NAME_PLACEHOLDER
        )
        return self.replace_placeholder(components_suffix, class_name, HYPHEN_PLACEHOLDER)

    def get_template_content(self, file_type):
        template_path = os.path.join(TEMPLATES_DIR, self.get_template_filename(file_type))
        return open(template_path, 'r').read()

    @staticmethod
    def get_component_suffix(filename):
        identifier = filename and filename.split('.')[1]
        if identifier and identifier in COMPONENT_SUFFIX_DICTIONARY:
            return COMPONENT_SUFFIX_DICTIONARY[identifier]
        else:
            return ''

    @staticmethod
    def get_css_filename(filename):
        return '{}.scss'.format('.'.join(filename.split('.')[:-1]))

    @staticmethod
    def get_state_path(folder_path, filename, file_type):
        return os.path.join(folder_path, '{}.{}.js'.format(filename, file_type))

    @staticmethod
    def replace_placeholder(content, class_name, placeholder):
        return content.replace(placeholder, class_name)

    @staticmethod
    def get_template_filename(file_type):
        files = os.listdir(os.path.abspath(TEMPLATES_DIR))
        for f in files:
            if f.split('.')[0] == file_type:
                return f

    @staticmethod
    def get_camel_case_string(filename):
        words = filename.split('-')
        return words[0].capitalize() + ''.join(word.capitalize() for word in words[1:])

    @staticmethod
    def get_full_path(filename):
        return '{}\{}'.format(SCRIPT_PATH, filename)

    @staticmethod
    def log(origin, message):
        print (SEPARATOR)
        print ('{} -> {}'.format(origin, message))

    @staticmethod
    def abort():
        sys.exit(MESSAGES.get('aborted'))
