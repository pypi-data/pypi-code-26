from pathlib import Path
from typing import List


class DockerRunBuilder:

    DOCKER_CMD = 'docker'
    DOCKER_COMPOSE_CMD = 'docker-compose'
    ARG_VOLUME = '-v'
    ARG_ENVIRONMENT = '-e'
    ARG_REMOVE = '--rm'

    def __init__(self, image_name: str):
        self._image_name = image_name
        self._volumes = {}
        self._environments = {}
        self._passed_environments = []
        self._remove = False
        self._use_bash = False

    def volume(self, host_path, mount, read_only=False):
        self._volumes[host_path] = {'mount': mount, 'read_only': read_only}
        return self

    def environment(self, name, value):
        self._environments[name] = value
        return self

    def pass_environment(self, name):
        self._passed_environments.append(name)
        return self

    def auto_remove(self):
        self._remove = True
        return self

    def in_bash(self):
        self._use_bash = True
        return self

    def build(self, command):
        command_parts = [f'{self.DOCKER_CMD} run']

        command_parts += [a for a in self.__get_arguments()]

        return self.__build_command(command_parts, command)

    def build_compose(self,
                      command,
                      compose_file: Path,
                      additional_files: List[Path] = None):

        command_parts = [f'{self.DOCKER_COMPOSE_CMD} run']

        command_parts += [a for a in self.__get_arguments()]
        command_parts += map(lambda p: f'-f {p}',
                             [compose_file]
                             + (additional_files if additional_files else []))

        return self.__build_command(command_parts, command)

    def __build_command(self, command_parts, command):
        command_parts.append(self.ARG_REMOVE) if self._remove is True else None
        command_parts.append(self._image_name)

        bash_pre = 'bash -c "' if self._use_bash is True else ''
        bash_post = '"' if self._use_bash is True else ''
        command_parts.append(f'{bash_pre}{command}{bash_post}')

        return ' '.join(command_parts).strip()

    def __get_arguments(self):
        for host_path in self._volumes:
            yield f'{self.ARG_VOLUME} ' \
                  f'{host_path}:{self._volumes[host_path]["mount"]}' \
                  f'{":ro" if self._volumes[host_path]["read_only"] is True else ""}'

        for environment in self._environments:
            yield f'{self.ARG_ENVIRONMENT} ' \
                  f'{environment}={self._environments[environment]}'
        for environment in self._passed_environments:
            yield f'{self.ARG_ENVIRONMENT} {environment}'
