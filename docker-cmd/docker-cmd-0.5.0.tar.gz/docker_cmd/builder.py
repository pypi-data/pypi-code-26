import os

class DockerRunBuilder:

    DOCKER_CMD = 'docker'
    ARG_VOLUME = '-v'
    ARG_ENVIRONMENT = '-e'
    ARG_REMOVE = '--rm'

    def __init__(self, image_name: str):
        self._image_name = image_name
        self._volumes = {}
        self._environments = {}
        self._remove = False
        self._use_bash = False

    def volume(self, host_path, mount, read_only=False):
        self._volumes[host_path] = {'mount': mount, 'read_only': read_only}
        return self

    def environment(self, name, value):
        self._environments[name] = value
        return self

    def pass_environment(self, name):
        self._environments[name] = os.environ[name]
        return self

    def auto_remove(self):
        self._remove = True
        return self

    def in_bash(self):
        self._use_bash = True
        return self

    def build(self, command):
        command_parts = [
            'docker run'
        ]

        for host_path in self._volumes:
            command_parts.append(f'{self.ARG_VOLUME} '
                                 f'{host_path}:{self._volumes[host_path]["mount"]}'
                                 f'{":ro" if self._volumes[host_path]["read_only"] is True else ""}')

        for environment in self._environments:
            command_parts.append(f'{self.ARG_ENVIRONMENT} '
                                 f'{environment}={self._environments[environment]}')

        command_parts.append(self.ARG_REMOVE) if self._remove is True else None

        command_parts.append(self._image_name)

        bash_pre = 'bash -c "' if self._use_bash is True else ''
        bash_post = '"' if self._use_bash is True else ''
        command_parts.append(f'{bash_pre}{command}{bash_post}')

        return ' '.join(command_parts).strip()
