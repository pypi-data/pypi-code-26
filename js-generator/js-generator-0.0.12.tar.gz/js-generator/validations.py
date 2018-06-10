from constants import MESSAGES, FOLDER_REQUIRED, FILENAME_REQUIRED
import os
from utils import Utils

utils = Utils()


class Validations:
    def __init__(self):
        pass

    def validate(self, args):
        self.validate_class_name(args.classname)

        if args.type in FILENAME_REQUIRED:
            self.validate_has_filename(args.filename)

        if args.type in FOLDER_REQUIRED or args.full_state:
            if self.is_file_exists(args.classname):
                self.exit('[validate]', MESSAGES.get('folder_exists').format(args.classname))

            else:
                return 1

        else:
            self.validate_file_exists(args.filename)
            self.validate_type(args.type)
            return 1

    def validate_has_filename(self, filename):
        if not filename:
            self.exit('[validate_has_filename]', MESSAGES.get('error_no_filename'))

    def validate_file_exists(self, filename):
        if self.is_file_exists(filename):
            text = raw_input(MESSAGES.get('override'))
            if str(text) != 'y':
                utils.abort()
                return 0
            else:
                return 1
        else:
            return 1

    def validate_class_name(self, class_name):
        if class_name:
            return class_name
        else:
            self.exit('[validate_class_name]', MESSAGES.get('error_no_class_name'))

    def validate_type(self, file_type):
        template = utils.get_template_filename(file_type)
        if template:
            return template
        else:
            self.exit('[create_file]', MESSAGES.get('error_no_template_found').format(file_type))

    @staticmethod
    def is_file_exists(filename):
        full_path = utils.get_full_path(filename)
        return os.path.isfile(full_path) or os.path.isdir(full_path)

    @staticmethod
    def exit(function_name, error_message):
        utils.log(function_name, error_message)
        utils.abort()

