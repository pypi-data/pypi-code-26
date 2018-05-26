"""
Profile subcommand
"""
import os
import tempfile

import yaml

from .base import BaseSubcommand

from compose_flow.compose import get_overlay_filenames
from compose_flow.config import get_config
from compose_flow.errors import EnvError, NoSuchConfig, NoSuchProfile, ProfileError
from compose_flow.utils import remerge, render

COPY_ENV_VAR = 'CF_COPY_ENV_FROM'

# keep track of written profiles in order to prevent writing them twice
WRITTEN_PROFILES = []


def dump_yaml(data):
    return yaml.dump(data, default_flow_style=False)


def get_kv(item: str) -> tuple:
    """
    Returns the item split at equal
    """
    item_split = item.split('=', 1)
    key = item_split[0]

    try:
        val = item_split[1]
    except IndexError:
        val = None

    return key, val


def listify_kv(d: dict) -> list:
    """
    Returns an equal-delimited list of the dictionary's key/value pairs

    When the value is null the equal is not appended
    """
    return [f'{k}={v}' if v else k for k, v in d.items()]


class Profile(BaseSubcommand):
    """
    Subcommand for managing profiles
    """
    @property
    def filename(self) -> str:
        """
        Returns the filename for this profile
        """
        return f'compose-flow-{self.args.profile}.yml'

    @classmethod
    def fill_subparser(cls, parser, subparser):
        subparser.add_argument('action')

    def cat(self):
        """
        Prints the loaded compose file to stdout
        """
        print(self.load())

    def check(self):
        """
        Checks the profile against some rules
        """
        env_data = self.env.data

        compose_content = self.load()
        data = yaml.load(compose_content)

        errors = []
        for name, service_data in data['services'].items():
            for item in service_data.get('environment', []):
                # when a variable has an equal sign, it is setting
                # the value, so don't check the environment for this variable
                if '=' in item:
                    continue

                if item not in env_data:
                    errors.append(f'{item} not found in environment')

        if errors:
            raise ProfileError('\n'.join(errors))

    def _copy_environment(self, content):
        """
        Processes CF_COPY_ENV_FROM environment entries
        """
        # load up the yaml
        data = yaml.load(content)
        environments = {}

        # first get the env from each service
        for service_name, service_data in data['services'].items():
            environment = service_data.get('environment')
            if environment:
                _env = {}

                for item in environment:
                    k, v = get_kv(item)

                    _env[k] = v

                environments[service_name] = _env

        # go through each service environment and apply any copies found
        for service_name, service_data in data['services'].items():
            environment = service_data.get('environment')
            if not environment:
                continue

            new_env = {}
            for item in environment:
                key, val = get_kv(item)
                new_env[key] = val

                if not item.startswith(COPY_ENV_VAR):
                    continue

                _env = environments.get(val)
                if not _env:
                    raise EnvError(f'Unable to find val={val} to copy into service_name={service_name}')

                new_env.update(_env)

            service_data['environment'] = listify_kv(new_env)

        return dump_yaml(data)

    def get_profile_compose_file(self, profile):
        """
        Processes the profile to generate the compose file
        """
        try:
            os.environ.update(self.env.data)
        except NoSuchConfig as exc:
            if not self.workflow.subcommand.is_env_error_okay(exc):
                raise

        filenames = get_overlay_filenames(profile)

        # merge multiple files together so that deploying stacks works
        # https://github.com/moby/moby/issues/30127
        if len(filenames) > 1:
            yaml_contents = []

            for item in filenames:
                with open(item, 'r') as fh:
                    yaml_contents.append(yaml.load(fh))

            merged = remerge(yaml_contents)
            content = dump_yaml(merged)
        else:
            with open(filenames[0], 'r') as fh:
                content = fh.read()

        content = self._copy_environment(content)

        fh = tempfile.TemporaryFile(mode='w+')

        # render the file
        try:
            rendered = render(content)
        except EnvError as exc:
            if not self.workflow.subcommand.is_missing_profile_okay(exc):
                raise

            return fh

        fh.write(rendered)
        fh.flush()

        fh.seek(0, 0)

        return fh

    def load(self) -> str:
        """
        Loads the compose file that is generated from all the items listed in the profile
        """
        fh = self.get_profile_compose_file(self.profile_files)

        return fh.read()

    @property
    def profile_files(self) -> dict:
        """
        Returns the profile data found in the dc.yml file
        """
        config = get_config()

        profile_name = self.args.profile
        try:
            profile = config['profiles'][profile_name]
        except KeyError:
            raise NoSuchProfile(f'profile={profile_name}')

        return profile

    def write(self) -> None:
        """
        Writes the loaded compose file to disk
        """
        # do not write profiles more than once per execution
        if self.filename in WRITTEN_PROFILES:
            return

        with open(self.filename, 'w') as fh:
            fh.write(self.load())

        WRITTEN_PROFILES.append(self.filename)
