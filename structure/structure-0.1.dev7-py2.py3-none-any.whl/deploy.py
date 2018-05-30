import sys
import os
import zipfile

import pathspec

if sys.version_info[0] < 3:
    from config import ConfigManager
    from errors import Error
    from network import NetworkManager
    from utils import green
else:
    from structure.config import ConfigManager
    from structure.errors import Error
    from structure.network import NetworkManager
    from structure.utils import green

SRC_ZIP_NAME = 'src.zip'


def files_exists(src_path, files):
    for f in files:
        path = os.path.join(src_path, f)
        if os.path.isfile(path):
            return True
    return False


def guess_application_type(src_path):
    is_flask = files_exists(src_path, ['app.py'])
    is_node = files_exists(src_path, ['package.json'])
    is_docker = files_exists(src_path, ['Dockerfile'])
    is_static = files_exists(src_path, ['index.html'])

    # Intentionally exclude is_static for now
    count = sum([is_flask, is_node, is_docker])

    # No candidates other than static
    if count == 0:
        return 'static' if is_static else None

    # One clear candidate
    elif count == 1:
        if is_flask:
            return 'flask'
        elif is_node:
            return 'express'
        elif is_docker:
            return 'docker'

    # Multiple candidates
    return None


def is_restricted_directory(path):
    home_dir = os.path.expanduser('~')
    directories = [
        home_dir,
        os.path.join(home_dir, 'Desktop'),
        os.path.join(home_dir, 'Downloads'),
        os.path.join(home_dir, 'Documents'),
    ]

    for d in directories:
        if os.path.exists(d) and os.path.samefile(path, d):
            return True
    return False


class DeployManger(object):

    @staticmethod
    def default_ignored_files():
        return [
            "*.pyc",
            ".env",
            "env/",
            "venv/*",
            "venv",
            ".eggs",
            "node_modules",
            "node_modules/*",
            "*.zip",
            ".DS_STORE",
            "npm-debug.log*",
            "yarn-debug.log*",
            "yarn-error.log*",
            ".npm",
            ".ssh",
        ]

    @staticmethod
    def git_ignored_files(base_path):
        try:
            path = os.path.join(base_path, '.gitignore')
            if os.path.exists(path):
                with open(path) as gitignore:
                    lines = gitignore.readlines()

                    # Convert '\n' items to ''
                    lines = [x.strip() for x in lines]

                    # Remove '' items
                    lines = [x for x in lines if x]

                    # print(lines)
                    return lines
            return []
        except:
            return []

    @staticmethod
    def archive_directory(src_path):
        zipf = zipfile.ZipFile(SRC_ZIP_NAME, 'w', zipfile.ZIP_DEFLATED)

        skip_rules = set(DeployManger.default_ignored_files())
        skip_rules.update(DeployManger.git_ignored_files(src_path))
        skip_rules = list(skip_rules)

        spec = pathspec.PathSpec.from_lines(
            pathspec.patterns.GitWildMatchPattern,
            skip_rules
        )

        for root, _, files in os.walk(src_path):
            for file in files:
                abs_name = os.path.abspath(os.path.join(root, file))
                arc_name = abs_name[len(src_path) + 1:]

                should_ignore = len(list(spec.match_files([arc_name]))) > 0
                if not should_ignore:
                    zipf.write(os.path.join(root, file), arcname=arc_name)
                else:
                    pass
                    # print("Ignoring: {}".format(arc_name))

        zipf.close()

    @staticmethod
    def deploy(app=None, type=None, reload=False):

        config = ConfigManager.get_app_config()
        src_path = os.getcwd()

        if not app:
            if not config:
                print(Error.warn('Please provide either an app name to deploy to, or create a structure.yaml file.'))
                return
            elif not 'name' in config:
                print(Error.warn('No application name specified in your structure.yaml file.'))
                return
            else:
                app = config['name']

        print("Deploying to {}...".format(green(app)))

        if not type:
            if config and 'type' in config:
                type = config['type']
                print("Application type: {}".format(green(type)))
            else:
                guess = guess_application_type(src_path)

                if guess:
                    type = guess
                    print("Detected application type: {}".format(guess))
                else:
                    type_string = green('--type')
                    print(Error.warn(
                        'Please specify an application type either with the {} argument, or via a structure.yaml file.'.format(type_string)))
                    return

        # Safety check.
        if is_restricted_directory(src_path):
            return Error.error("  You're trying to deploy a protected folder; please choose a different folder.")

        DeployManger.archive_directory(src_path)

        zip_file = open(SRC_ZIP_NAME, 'rb')

        files = {
            SRC_ZIP_NAME: zip_file,
        }

        response = NetworkManager.POST_JSON(
            endpoint='/cli/{}/deploy/{}'.format(app, type),
            files=files,
        )

        os.remove(SRC_ZIP_NAME)

        try:
            success = response['success']
            if success:
                return green('\n  Deploy complete! \n')
            else:
                message = response['message']
                if message:
                    return Error.error(message)
        except Exception as e:
            return e

        return 'Unable to deploy.'
