from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import input

import os
import subprocess
import sys

from publisher import settings
from publisher.exceptions import SingleProceduresNotFoundError


DEFAULT_INPUT_READER = input


def get_content_directories(root_directory):

    def is_content_directory(d):
        ignored_directories = ['assets', 'translations', 'build_assets']
        return os.path.isdir(os.path.join(root_directory, d)) and d not in ignored_directories and not d.startswith('.')

    return [d for d in os.listdir(root_directory) if is_content_directory(d)]


class WorkingDirectory(object):
    """ Context manager for changing directory"""
    def __init__(self, new_dir):
        self.new_dir = new_dir
        self.old_dir = None

    def __enter__(self):
        self.old_dir = os.getcwd()
        os.chdir(self.new_dir)

    def __exit__(self, *_):
        os.chdir(self.old_dir)


def get_procedure_code():

    procedure_directories = get_content_directories(settings.PROCEDURE_CHECKOUT_DIRECTORY)

    if len(procedure_directories) != 1:
        raise SingleProceduresNotFoundError()

    return procedure_directories[0]


def get_user_commit_selection(message, objects, result_accessor=None):
    result_accessor = result_accessor or DEFAULT_INPUT_READER

    for number, obj in enumerate(objects):
        print('{0}:'.format(number + 1), str(obj))

    print(message)
    sys.stdout.flush()

    user_input = int(result_accessor(''))

    if 1 <= user_input <= len(objects):
        return objects[user_input - 1]

    if user_input == 0:
        print("Operation cancelled.")

    else:
        print("Invalid option selected.")

    return None


def get_command_output(command_args):
    command = subprocess.Popen(command_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = command.communicate()
    return output.decode("utf8"), error.decode("utf8")


def get_yes_no(message=''):
    user_response = DEFAULT_INPUT_READER(message)
    if user_response == 'y':
        return True
    return False


def get_input(message=''):
    user_response = DEFAULT_INPUT_READER(message)
    return user_response


def get_platform():
    return sys.platform.lower()
