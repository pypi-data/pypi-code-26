import argparse
import os
import sys

from .cli import CommandLineInterface, logger

name = "appset"

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-v', '--debug', required=False, action='store_true')
parser.add_argument('-h', '--help', required=False, action='store_true')
parser.add_argument('-p', '--param', required=False, action='append')
parser.add_argument('-e', '--env', required=True, default='')
parser.add_argument('-m', '--modules', required=True, default='')
parser.add_argument('command', nargs='*')

pwd = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
env_vars = {}


def get_env(required_env):
    for env in required_env:
        env_vars[env] = os.environ.get(env)
    if not all(env_vars.values()):
        logger.error('Some secrets are missing. Place following environment variables in dotenv file:')
        for var in env_vars.keys():
            logger.info(var)
        sys.exit(1)
    return env_vars


def load_env(envfile_path):
    abs_path = os.path.abspath(envfile_path) if envfile_path else f'{pwd}/.env'
    if not os.path.exists(abs_path):
        logger.error(f'File {abs_path} does not exist. Create it or provide another file with --env flag.')
        sys.exit(1)
    env_files = (f'{abs_path}/{file}' for file in os.listdir(abs_path) if file.endswith('.env')) if os.path.isdir(
        abs_path) else [abs_path]
    for file in env_files:
        with open(file) as opened_file:
            for line in opened_file:
                env, var = line.split("=")
                os.environ[env] = var.rstrip()


def load_modules(modules_path):
    modules_abs_path = os.path.abspath(modules_path)
    logger.debug(f'Try to load modules from {modules_abs_path}')
    if not os.path.isdir(modules_abs_path):
        logger.error(f'{modules_abs_path} could not be found as modules\' source')
        sys.exit(1)
    modules_dir_name = modules_abs_path.split('/')[-1]
    modules_parent_path = modules_abs_path[:-len(modules_dir_name)]
    return modules_dir_name, modules_parent_path


def execute(command):
    args = parser.parse_args(command)
    load_env(args.env)
    modules_dir, modules_parent_path = load_modules(args.modules)
    appset_cli = CommandLineInterface(modules_dir=modules_dir, modules_parent_path=modules_parent_path,
                                      debug=args.debug)
    appset_cli.run_command(command=args.command, params=args.param, run_help=args.help)
