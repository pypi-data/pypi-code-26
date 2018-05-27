#!/usr/bin/python
# -*- coding: UTF-8 -*-
r"""
@author: Martin Klapproth <martin.klapproth@googlemail.com>
"""
from getpass import getpass
import logging
import socket
import stat
import textwrap
import sys
import posixpath
from stat import S_ISDIR, S_ISREG
from uuid import uuid1
import os.path

import paramiko
from paramiko.transport import SSHException

from remotelib.exceptions import AuthenticationFailedException, NetworkException
import remotelib
from remotelib.result import ExecutionResult
from remotelib.script import Script

logger = logging.getLogger(__name__)
# logging.getLogger("paramiko.transport").setLevel(logging.INFO)

ssh_config_files = [
    # os.path.expanduser("~/.ssh/config")
]

ssh_config = paramiko.SSHConfig()

if sys.version_info[0] == 2:
    # this builtin class does only exist in python 3
    class FileNotFoundError(Exception):
        pass
    class ConnectionRefusedError(Exception):
        pass

def read_ssh_config(path):
    with open(path) as f:
        ssh_config.parse(f)


user_config_file = os.path.expanduser("~/.ssh/config")
if os.path.exists(user_config_file):
    read_ssh_config(user_config_file)


def format_env(env):
    items = []

    for key, value in env.items():
        items.append("%s=%s" % (key, value))

    return " ".join(items)


def wrap_sudo(cmd, user):
    return "su - %s -c '%s'" % (user, cmd.replace('"', '\\"'))

import atexit
def close_all_connection():
    for _, conn in Host.connection_cache.items():
        # logger.info("Closing connection: %s" % conn)
        conn.close()

atexit.register(close_all_connection)


class Host:
    """
    vm = Host("ovz3")
    vm.port = PORT
    vm.key_filename = "/home/martin/.ssh/asdf"

    # install node
    vm.exec_script(Script.from_file("scripts/install_nodejs.sh"), timeout=600)
    vm.exec("apt-get install -y git")
    """
    connection_cache = {}

    def __init__(self, address, user="root", password=None, port=22, timeout=10, prompt=False, key_filename=None):
        self.address = address
        self.timeout = timeout

        cfg = ssh_config.lookup(self.address)
        self.hostname = cfg.get("hostname", self.address)
        self.port = int(cfg.get("port", port))
        self.user = cfg.get("user", user)

        self.key_filename = key_filename
        if not self.key_filename and "identityfile" in cfg:
            self.key_filename = cfg["identityfile"][0]

        self.password = password
        self.prompt = prompt
        if prompt:
            self.prompt_password()

        self._ssh_client = None
        self._ftp = None

    def append_file(self, fname, data: str, strip=True, dedent=True):
        """

        :param fname:
        :param data:
        :return:
        """
        if strip:
            data = data.strip()

        if dedent:
            data = textwrap.dedent(data)

        f = self.ftp.open(fname, "a")
        f.write(data)
        f.close()

    def chown(self, path, uid, gid):
        if type(uid) == str:
            uid = int(uid)
        if type(gid) == str:
            gid = int(gid)
        return self.ftp.chown(path, uid, gid)

    def chmod(self, path, mode):
        if type(mode) == str:
            mode = int(mode, 8)
        return self.ftp.chmod(path, mode)

    def connect(self):
        """
        :raises: AuthenticationFailedException, ConnectionRefusedError
        :return:
        """
        connection_doc = dict(
            hostname=self.hostname,
            username=self.user,
            password=self.password,
            port=self.port,
            key_filename=self.key_filename,
        )

        connection_id = hash(frozenset(connection_doc.items()))

        if connection_id in self.connection_cache:
            logger.info("Using cached connection")
            self._ssh_client = self.connection_cache[connection_id]
            return self.connection_cache[connection_id]

        logger.info("connecting to %s@%s:%s" % (self.user, self.hostname, self.port) +
                    (" using key file %s" % self.key_filename if self.key_filename else ""))

        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self._ssh_client.connect(
                timeout=self.timeout,
                **connection_doc
            )
            if self._ssh_client:
                self.connection_cache[connection_id] = self._ssh_client
        except paramiko.ssh_exception.AuthenticationException as e:
            logger.error("%s: Authentication failed" % self.hostname)
            if self.prompt:
                self.prompt_password()
                self.connect()
            else:
                raise AuthenticationFailedException()
        except paramiko.ssh_exception.SSHException as e:
            return AuthenticationFailedException(str(e))
        except socket.timeout as e:
            logger.error("socket.timeout: %s: %s" % (self.hostname, e))
            raise NetworkException("Socket Timeout")
        except ConnectionRefusedError as e:
            logger.error("connection refused: host=%s, port=%s" % (self.hostname, self.port))
            raise NetworkException("Connection Refused")
        except socket.gaierror as e:
            raise NetworkException(str(e))


    def disconnect(self):
        if self._ftp:
            self._ftp.close()
        if self._ssh_client:
            self._ssh_client.close()

    def download(self, remotepath, localpath=None):
        if not localpath:
            localpath = posixpath.basename(remotepath)

        return self.ftp.get(remotepath, localpath)

    def execute(self, command, timeout=300, cwd=None, env=None, interactive=False, sudo=None):
        """

        @param command:
        @type command: str
        @param timeout:
        @type timeout: int
        @param cwd:
        @type cwd: str
        @param env:
        @type env: dict
        @param interactive:
        @type interactive: bool
        @param sudo:
        @type sudo: str
        @return:
        @rtype: ExecutionResult
        """
        if not env:
            env = {}

        cmd = [
            "%s %s" % (format_env(env), command)
        ]

        if cwd:
            cmd.insert(0, "cd %s" % cwd)

        cmd = "; ".join(cmd).strip()
        if sudo:
            cmd = "su - %s -c '%s'" % (sudo, cmd.replace('"', '\\"'))

        # do not modify cmd below this line
        logger.info("execute command on %s: '%s' (timeout=%s)" % (self.hostname, cmd, timeout))

        bufsize = -1

        chan = self.ssh_client.get_transport().open_session()
        chan.settimeout(timeout)
        chan.exec_command(cmd)

        if interactive:
            chan.set_combine_stderr(True)

        stdin = chan.makefile('wb', bufsize)
        stdout = chan.makefile('r', bufsize)
        stderr = chan.makefile_stderr('r', bufsize)

        if interactive:
            out = stdout.readline()
            while out:
                sys.stdout.write(out)
                sys.stdout.flush()
                out = stdout.readline()

        result = ExecutionResult()
        result.command = command
        result.stdin_stream = stdin
        result.stdout_stream = stdout
        result.stderr_stream = stderr
        result.exit_status = stdout.channel.recv_exit_status()

        logger.info("Command returned exit status %s" % result.exit_status)

        remotelib._policy.handle_result(result)

        return result

    def exec_file(self, path, *args, **kwargs):
        script = Script.from_file(path)
        return self.exec_script(script, *args, **kwargs)

    def exec_script(self, script, timeout=300, cwd=None, env=None, sudo=None, **kwargs):
        if not isinstance(script, Script):
            script = Script(script)

        logger.info("executing script on host %s: %s" % (self.hostname, script.content.strip()[:20]+"..."))

        if not env:
            env = {}

        path = "/tmp/rmlib_%s" % uuid1()

        with self.ftp.open(path, "w") as f:
            logger.debug("uploading script: %s" % path)
            f.write(script.content)

        cmd = "%s %s" % (format_env(env), path)
        if cwd:
            cmd = "cd %s" % cwd + ";" + cmd
        if sudo:
            cmd = wrap_sudo(cmd, sudo)

        cmd = [
            "chmod 777 %s" % path,
            cmd
        ]

        r = self.execute("; ".join(cmd), timeout=timeout, **kwargs)

        self.ftp.remove(path)

        return r

    @property
    def ftp(self):
        try:
            self._ftp = self.ssh_client.open_sftp()
        except SSHException as e:
            self.ssh_client.close()
            self.connect()
            self._ftp = self.ssh_client.open_sftp()

        return self._ftp

    def mkdir(self, path, mode=0o755, recurse=False):
        def mkdir_p(sftp, remote_directory):
            """Change to this directory, recursively making new folders if needed.
            Returns True if any folders were created."""
            if remote_directory == '/':
                # absolute path so change directory to root
                sftp.chdir('/')
                return
            if remote_directory == '':
                # top-level relative directory must exist
                return
            try:
                sftp.chdir(remote_directory) # sub-directory exists
            except IOError:
                dirname, basename = os.path.split(remote_directory.rstrip('/'))
                mkdir_p(sftp, dirname) # make parent directories
                sftp.mkdir(basename, mode=mode) # sub-directory missing, so created it
                sftp.chdir(basename)
                return True

        if recurse:
            return mkdir_p(self.ftp, path)

        try:
            self.ftp.mkdir(path, mode=mode)
        except IOError as e:
            # will be raised if directory exists
            if self.isdir(path):
                return True
            else:
                raise e

    def prompt_password(self):
        self.password = getpass("Password for %s@%s: " % (self.user, self.hostname))

    @property
    def ssh_client(self):
        if not self._ssh_client:
            self.connect()

        return self._ssh_client

    def isfile(self, remotepath, stat=None):
        if not stat:
            try:
                stat = self.ftp.stat(remotepath)
            # python3
            except FileNotFoundError:
                return False
            # python2
            except IOError:
                return False

        return S_ISREG(stat.st_mode)

    def isdir(self, remotepath, stat=None):
        if not stat:
            try:
                stat = self.ftp.stat(remotepath)
            # python3
            except FileNotFoundError:
                return False
            # python2
            except IOError:
                return False

        return S_ISDIR(stat.st_mode)

    def listdir(self, path):
        return self.ftp.listdir(path)

    def read_file(self, fname):
        """
        Returns the contents of <fname> as str.
        
        :param fname:
        :param data:
        :return:
        """
        f = self.ftp.open(fname, "rb")
        c = f.read()
        f.close()
        return c

    def remove(self, fname, *args, **kwargs):
        """
        Removes a single file.

        :param fname:
        :param args:
        :param kwargs:
        :return:
        """
        return self.ftp.remove(fname, *args, **kwargs)

    def rmdir(self, fname, *args, **kwargs):
        """
        Removes an empty directory

        :param fname:
        :param args:
        :param kwargs:
        :return:
        """
        return self.ftp.rmdir(fname, *args, **kwargs)

    def rmtree(self, remotepath, level=0):
        """
        Behaves like "rm -rf <remotepath>"

        :param remotepath:
        :param level:
        :return:
        """
        for f in self.ftp.listdir_attr(remotepath):
            rpath = posixpath.join(remotepath, f.filename)
            if stat.S_ISDIR(f.st_mode):
                self.rmtree(rpath, level=(level + 1))
            else:
                rpath = posixpath.join(remotepath, f.filename)
                # print('removing %s%s' % ('    ' * level, rpath))
                self.ftp.remove(rpath)
        # print('removing %s%s' % ('    ' * level, remotepath))
        self.ftp.rmdir(remotepath)

    def stat(self, remotepath):
        return self.ftp.stat(remotepath)

    def upload(self, localpath, remotepath, mode=None):
        """
        host.upload("foo.txt", "/tmp") # will upload to /tmp/foo.txt
        host.upload("foo.txt", "/tmp/bar") # will upload to /tmp/bar or /tmp/bar/foo.txt if /tmp/bar is a directory

        :param localpath:
        :param remotepath:
        :return:
        """
        if self.isdir(remotepath):
            remotepath = os.path.join(remotepath, localpath.split("/")[-1])

        self.ftp.put(localpath, remotepath)

        if mode:
            self.execute("chmod %s %s" % (mode, remotepath))

    def write_file(self, fname, data: bytes, dedent=True, strip=True, mod=None):
        """

        :param fname:
        :param data:
        :return:
        """
        if type(data) == str:
            if dedent:
                data = textwrap.dedent(data)
            if strip:
                data = data.strip()

        f = self.ftp.open(fname, "wb")
        f.write(data)
        f.close()

        if mod:
            self.chmod(fname, mod)

# for API compatibility
if sys.version_info[0] == 3:
    setattr(Host, "exec", Host.execute)
