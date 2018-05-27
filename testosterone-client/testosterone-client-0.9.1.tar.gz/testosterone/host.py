#!/usr/bin/python
# -*- coding: UTF-8 -*-
r"""
@author: Martin Klapproth <martin.klapproth@googlemail.com>
"""

import logging

from jinja2 import Template

from remotelib.host import Host as RemoteHost
from remotelib.result import ExecutionResult
from testosterone.config import Config
from testosterone.runner import TestosteroneRunner

logger = logging.getLogger(__name__)

HOST_REGISTRY = {}


class ExecutionResultWrapper(ExecutionResult):
    def __init__(self):
        super(ExecutionResultWrapper, self).__init__()
        self.host = None # type: HostWrapper
        self._stdout = None
        self._stderr = None

    def assert_success(self):
        assert self.exit_status == 0, "Command '%s' exited with return code '%s' on %s" % (self.command, self.exit_status, self.host.address) + "\n" + self.stdout + self.stderr
        return self

    def assert_contains(self, text):
        assert text in self.stdout, "Command output does not contain '%s'" % text + ", stdout:\n" + self.stdout
        return self

    def print(self):
        print(self.stdout)
        return self

    @property
    def stdout(self):
        """
        @rtype: str
        @return:
        """
        if not self._stdout:
            self._stdout = self.stdout_stream.read().decode("utf-8")
        return self._stdout
    
    @property
    def stderr(self):
        """
        @rtype: str
        @return:
        """
        if not self._stderr:
            self._stderr = self.stderr_stream.read().decode("utf-8")
        return self._stderr

class HostWrapper(RemoteHost):
    def __init__(self, *args, **kwargs):
        super(HostWrapper, self).__init__(*args, **kwargs)
        self.name = None

    def read_file(self, fname, mode="t"):
        result = super(HostWrapper, self).read_file(fname)
        if type(result) == bytes and mode == "t":
            result = result.decode()
        return result

    def assert_file_exists(self, name):
        assert self.isfile(name), "The file %s does not exist on %s" % (name, self.address)
        return self

    def execute(self, command, *args, **kwargs):
        """

        @param args:
        @param kwargs:
        @return:
        @rtype: ExecutionResultWrapper
        """
        if "{{" in command or "{%" in command:
            config = TestosteroneRunner.get_instance().config
            host_config = config["hosts"][self.name]
            context = {
                "config": config,
                "host": host_config
            }
            command = Template(command).render(**context)

        result = super(HostWrapper, self).execute(command, *args, **kwargs)
        new_result = ExecutionResultWrapper()
        new_result.host = self
        new_result.command = result.command
        new_result.stdin_stream = result.stdin_stream
        new_result.stdout_stream = result.stdout_stream
        new_result.stderr_stream = result.stderr_stream
        new_result.exit_status = result.exit_status
        return new_result


def Host(name):
    """
    @type name: str
    @rtype: HostWrapper
    """
    if name in HOST_REGISTRY:
        return HOST_REGISTRY[name]
    
    try:
        host_config = TestosteroneRunner.get_instance().config["hosts"][name]
    except KeyError:
        print("Host '%s' is not configured" % name)
        exit(3)
        return

    host = HostWrapper(
        address=host_config["host"],
        user=host_config.get("user", "root"),
        password=host_config.get("password"),
        port=int(host_config.get("port", 22)),
        timeout=int(host_config.get("timeout", 10)),
        prompt=False,
        key_filename=host_config.get("key"),
    )

    host.name = name

    HOST_REGISTRY[name] = host
    return host
