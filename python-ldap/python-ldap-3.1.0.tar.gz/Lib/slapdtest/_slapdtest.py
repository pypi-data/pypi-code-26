# -*- coding: utf-8 -*-
"""
slapdtest - module for spawning test instances of OpenLDAP's slapd server

See https://www.python-ldap.org/ for details.
"""

from __future__ import unicode_literals

import os
import socket
import sys
import time
import subprocess
import logging
import atexit
from logging.handlers import SysLogHandler
import unittest

# Switch off processing .ldaprc or ldap.conf before importing _ldap
os.environ['LDAPNOINIT'] = '1'

import ldap
from ldap.compat import quote_plus, which

HERE = os.path.abspath(os.path.dirname(__file__))

# a template string for generating simple slapd.conf file
SLAPD_CONF_TEMPLATE = r"""
serverID %(serverid)s
moduleload back_%(database)s
%(include_directives)s
loglevel %(loglevel)s
allow bind_v2

authz-regexp
  "gidnumber=%(root_gid)s\\+uidnumber=%(root_uid)s,cn=peercred,cn=external,cn=auth"
  "%(rootdn)s"

database %(database)s
directory "%(directory)s"
suffix "%(suffix)s"
rootdn "%(rootdn)s"
rootpw "%(rootpw)s"

TLSCACertificateFile "%(cafile)s"
TLSCertificateFile "%(servercert)s"
TLSCertificateKeyFile "%(serverkey)s"
# ignore missing client cert but fail with invalid client cert
TLSVerifyClient try

authz-regexp
    "C=DE, O=python-ldap, OU=slapd-test, CN=([A-Za-z]+)"
    "ldap://ou=people,dc=local???($1)"

"""

LOCALHOST = '127.0.0.1'

CI_DISABLED = set(os.environ.get('CI_DISABLED', '').split(':'))
if 'LDAPI' in CI_DISABLED:
    HAVE_LDAPI = False
else:
    HAVE_LDAPI = hasattr(socket, 'AF_UNIX')


def identity(test_item):
    """Identity decorator

    """
    return test_item


def skip_unless_ci(reason, feature=None):
    """Skip test unless test case is executed on CI like Travis CI
    """
    if not os.environ.get('CI', False):
        return unittest.skip(reason)
    elif feature in CI_DISABLED:
        return unittest.skip(reason)
    else:
        # Don't skip on Travis
        return identity


def requires_tls():
    """Decorator for TLS tests

    Tests are not skipped on CI (e.g. Travis CI)
    """
    if not ldap.TLS_AVAIL:
        return skip_unless_ci("test needs ldap.TLS_AVAIL", feature='TLS')
    else:
        return identity


def requires_sasl():
    if not ldap.SASL_AVAIL:
        return skip_unless_ci(
            "test needs ldap.SASL_AVAIL", feature='SASL')
    else:
        return identity


def requires_ldapi():
    if not HAVE_LDAPI:
        return skip_unless_ci(
            "test needs ldapi support (AF_UNIX)", feature='LDAPI')
    else:
        return identity

def _add_sbin(path):
    """Add /sbin and related directories to a command search path"""
    directories = path.split(os.pathsep)
    if sys.platform != 'win32':
        for sbin in '/usr/local/sbin', '/sbin', '/usr/sbin':
            if sbin not in directories:
                directories.append(sbin)
    return os.pathsep.join(directories)

def combined_logger(
        log_name,
        log_level=logging.WARN,
        sys_log_format='%(levelname)s %(message)s',
        console_log_format='%(asctime)s %(levelname)s %(message)s',
    ):
    """
    Returns a combined SysLogHandler/StreamHandler logging instance
    with formatters
    """
    if 'LOGLEVEL' in os.environ:
        log_level = os.environ['LOGLEVEL']
        try:
            log_level = int(log_level)
        except ValueError:
            pass
    # for writing to syslog
    new_logger = logging.getLogger(log_name)
    if sys_log_format and os.path.exists('/dev/log'):
        my_syslog_formatter = logging.Formatter(
            fmt=' '.join((log_name, sys_log_format)))
        my_syslog_handler = logging.handlers.SysLogHandler(
            address='/dev/log',
            facility=SysLogHandler.LOG_DAEMON,
        )
        my_syslog_handler.setFormatter(my_syslog_formatter)
        new_logger.addHandler(my_syslog_handler)
    if console_log_format:
        my_stream_formatter = logging.Formatter(fmt=console_log_format)
        my_stream_handler = logging.StreamHandler()
        my_stream_handler.setFormatter(my_stream_formatter)
        new_logger.addHandler(my_stream_handler)
    new_logger.setLevel(log_level)
    return new_logger  # end of combined_logger()


class SlapdObject(object):
    """
    Controller class for a slapd instance, OpenLDAP's server.

    This class creates a temporary data store for slapd, runs it
    listening on a private Unix domain socket and TCP port,
    and initializes it with a top-level entry and the root user.

    When a reference to an instance of this class is lost, the slapd
    server is shut down.

    An instance can be used as a context manager. When exiting the context
    manager, the slapd server is shut down and the temporary data store is
    removed.

    .. versionchanged:: 3.1

        Added context manager functionality
    """
    slapd_conf_template = SLAPD_CONF_TEMPLATE
    database = 'mdb'
    suffix = 'dc=slapd-test,dc=python-ldap,dc=org'
    root_cn = 'Manager'
    root_pw = 'password'
    slapd_loglevel = 'stats stats2'
    local_host = '127.0.0.1'
    testrunsubdirs = (
        'schema',
    )
    openldap_schema_files = (
        'core.schema',
    )

    TMPDIR = os.environ.get('TMP', os.getcwd())
    if 'SCHEMA' in os.environ:
        SCHEMADIR = os.environ['SCHEMA']
    elif os.path.isdir("/etc/openldap/schema"):
        SCHEMADIR = "/etc/openldap/schema"
    elif os.path.isdir("/etc/ldap/schema"):
        SCHEMADIR = "/etc/ldap/schema"
    else:
        SCHEMADIR = None

    BIN_PATH = os.environ.get('BIN', os.environ.get('PATH', os.defpath))
    SBIN_PATH = os.environ.get('SBIN', _add_sbin(BIN_PATH))

    # time in secs to wait before trying to access slapd via LDAP (again)
    _start_sleep = 1.5

    # create loggers once, multiple calls mess up refleak tests
    _log = combined_logger('python-ldap-test')

    def __init__(self):
        self._proc = None
        self._port = self._avail_tcp_port()
        self.server_id = self._port % 4096
        self.testrundir = os.path.join(self.TMPDIR, 'python-ldap-test-%d' % self._port)
        self._schema_prefix = os.path.join(self.testrundir, 'schema')
        self._slapd_conf = os.path.join(self.testrundir, 'slapd.conf')
        self._db_directory = os.path.join(self.testrundir, "openldap-data")
        self.ldap_uri = "ldap://%s:%d/" % (LOCALHOST, self._port)
        if HAVE_LDAPI:
            ldapi_path = os.path.join(self.testrundir, 'ldapi')
            self.ldapi_uri = "ldapi://%s" % quote_plus(ldapi_path)
            self.default_ldap_uri = self.ldapi_uri
            # use SASL/EXTERNAL via LDAPI when invoking OpenLDAP CLI tools
            self.cli_sasl_external = ldap.SASL_AVAIL
        else:
            self.ldapi_uri = None
            self.default_ldap_uri = self.ldap_uri
            # Use simple bind via LDAP uri
            self.cli_sasl_external = False

        self._find_commands()

        if self.SCHEMADIR is None:
            raise ValueError('SCHEMADIR is None, ldap schemas are missing.')

        # TLS certs
        self.cafile = os.path.join(HERE, 'certs/ca.pem')
        self.servercert = os.path.join(HERE, 'certs/server.pem')
        self.serverkey = os.path.join(HERE, 'certs/server.key')
        self.clientcert = os.path.join(HERE, 'certs/client.pem')
        self.clientkey = os.path.join(HERE, 'certs/client.key')

    @property
    def root_dn(self):
        return 'cn={self.root_cn},{self.suffix}'.format(self=self)

    def _find_commands(self):
        self.PATH_LDAPADD = self._find_command('ldapadd')
        self.PATH_LDAPDELETE = self._find_command('ldapdelete')
        self.PATH_LDAPMODIFY = self._find_command('ldapmodify')
        self.PATH_LDAPWHOAMI = self._find_command('ldapwhoami')

        self.PATH_SLAPD = os.environ.get('SLAPD', None)
        if not self.PATH_SLAPD:
            self.PATH_SLAPD = self._find_command('slapd', in_sbin=True)
        self.PATH_SLAPTEST = self._find_command('slaptest', in_sbin=True)

    def _find_command(self, cmd, in_sbin=False):
        if in_sbin:
            path = self.SBIN_PATH
            var_name = 'SBIN'
        else:
            path = self.BIN_PATH
            var_name = 'BIN'
        command = which(cmd, path=path)
        if command is None:
            raise ValueError(
                "Command '{}' not found. Set the {} environment variable to "
                "override slapdtest's search path.".format(cmd, var_name)
            )
        return command

    def setup_rundir(self):
        """
        creates rundir structure

        for setting up a custom directory structure you have to override
        this method
        """
        os.mkdir(self.testrundir)
        os.mkdir(self._db_directory)
        self._create_sub_dirs(self.testrunsubdirs)
        self._ln_schema_files(self.openldap_schema_files, self.SCHEMADIR)

    def _cleanup_rundir(self):
        """
        Recursively delete whole directory specified by `path'
        """
        # cleanup_rundir() is called in atexit handler. Until Python 3.4,
        # the rest of the world is already destroyed.
        import os, os.path
        if not os.path.exists(self.testrundir):
            return
        self._log.debug('clean-up %s', self.testrundir)
        for dirpath, dirnames, filenames in os.walk(
                self.testrundir,
                topdown=False
            ):
            for filename in filenames:
                self._log.debug('remove %s', os.path.join(dirpath, filename))
                os.remove(os.path.join(dirpath, filename))
            for dirname in dirnames:
                self._log.debug('rmdir %s', os.path.join(dirpath, dirname))
                os.rmdir(os.path.join(dirpath, dirname))
        os.rmdir(self.testrundir)
        self._log.info('cleaned-up %s', self.testrundir)

    def _avail_tcp_port(self):
        """
        find an available port for TCP connection
        """
        sock = socket.socket()
        try:
            sock.bind((self.local_host, 0))
            port = sock.getsockname()[1]
        finally:
            sock.close()
        self._log.info('Found available port %d', port)
        return port

    def gen_config(self):
        """
        generates a slapd.conf and returns it as one string

        for generating specific static configuration files you have to
        override this method
        """
        include_directives = '\n'.join(
            'include "{schema_prefix}/{schema_file}"'.format(
                schema_prefix=self._schema_prefix,
                schema_file=schema_file,
            )
            for schema_file in self.openldap_schema_files
        )
        config_dict = {
            'serverid': hex(self.server_id),
            'schema_prefix':self._schema_prefix,
            'include_directives': include_directives,
            'loglevel': self.slapd_loglevel,
            'database': self.database,
            'directory': self._db_directory,
            'suffix': self.suffix,
            'rootdn': self.root_dn,
            'rootpw': self.root_pw,
            'root_uid': os.getuid(),
            'root_gid': os.getgid(),
            'cafile': self.cafile,
            'servercert': self.servercert,
            'serverkey': self.serverkey,
        }
        return self.slapd_conf_template % config_dict

    def _create_sub_dirs(self, dir_names):
        """
        create sub-directories beneath self.testrundir
        """
        for dname in dir_names:
            dir_name = os.path.join(self.testrundir, dname)
            self._log.debug('Create directory %s', dir_name)
            os.mkdir(dir_name)

    def _ln_schema_files(self, file_names, source_dir):
        """
        write symbolic links to original schema files
        """
        for fname in file_names:
            ln_source = os.path.join(source_dir, fname)
            ln_target = os.path.join(self._schema_prefix, fname)
            self._log.debug('Create symlink %s -> %s', ln_source, ln_target)
            os.symlink(ln_source, ln_target)

    def _write_config(self):
        """Writes the slapd.conf file out, and returns the path to it."""
        self._log.debug('Writing config to %s', self._slapd_conf)
        with open(self._slapd_conf, 'w') as config_file:
            config_file.write(self.gen_config())
        self._log.info('Wrote config to %s', self._slapd_conf)

    def _test_config(self):
        self._log.debug('testing config %s', self._slapd_conf)
        popen_list = [
            self.PATH_SLAPTEST,
            "-f", self._slapd_conf,
            '-u',
        ]
        if self._log.isEnabledFor(logging.DEBUG):
            popen_list.append('-v')
            popen_list.extend(['-d', 'config'])
        else:
            popen_list.append('-Q')
        proc = subprocess.Popen(popen_list)
        if proc.wait() != 0:
            raise RuntimeError("configuration test failed")
        self._log.info("config ok: %s", self._slapd_conf)

    def _start_slapd(self):
        """
        Spawns/forks the slapd process
        """
        urls = [self.ldap_uri]
        if self.ldapi_uri:
            urls.append(self.ldapi_uri)
        slapd_args = [
            self.PATH_SLAPD,
            '-f', self._slapd_conf,
            '-F', self.testrundir,
            '-h', ' '.join(urls),
        ]
        if self._log.isEnabledFor(logging.DEBUG):
            slapd_args.extend(['-d', '-1'])
        else:
            slapd_args.extend(['-d', '0'])
        self._log.info('starting slapd: %r', ' '.join(slapd_args))
        self._proc = subprocess.Popen(slapd_args)
        # Waits until the LDAP server socket is open, or slapd crashed
        # no cover to avoid spurious coverage changes, see
        # https://github.com/python-ldap/python-ldap/issues/127
        for _ in range(10):  # pragma: no cover
            if self._proc.poll() is not None:
                self._stopped()
                raise RuntimeError("slapd exited before opening port")
            time.sleep(self._start_sleep)
            try:
                self._log.debug(
                    "slapd connection check to %s", self.default_ldap_uri
                )
                self.ldapwhoami()
            except RuntimeError:
                pass
            else:
                return
        raise RuntimeError("slapd did not start properly")

    def start(self):
        """
        Starts the slapd server process running, and waits for it to come up.
        """

        if self._proc is None:
            # prepare directory structure
            atexit.register(self.stop)
            self._cleanup_rundir()
            self.setup_rundir()
            self._write_config()
            self._test_config()
            self._start_slapd()
            self._log.debug(
                'slapd with pid=%d listening on %s and %s',
                self._proc.pid, self.ldap_uri, self.ldapi_uri
            )

    def stop(self):
        """
        Stops the slapd server, and waits for it to terminate and cleans up
        """
        if self._proc is not None:
            self._log.debug('stopping slapd with pid %d', self._proc.pid)
            self._proc.terminate()
            self.wait()
        self._cleanup_rundir()
        if hasattr(atexit, 'unregister'):
            # Python 3
            atexit.unregister(self.stop)
        elif hasattr(atexit, '_exithandlers'):
            # Python 2, can be None during process shutdown
            try:
                atexit._exithandlers.remove(self.stop)
            except ValueError:
                pass

    def restart(self):
        """
        Restarts the slapd server with same data
        """
        self._proc.terminate()
        self.wait()
        self._start_slapd()

    def wait(self):
        """Waits for the slapd process to terminate by itself."""
        if self._proc:
            self._proc.wait()
            self._stopped()

    def _stopped(self):
        """Called when the slapd server is known to have terminated"""
        if self._proc is not None:
            self._log.info('slapd[%d] terminated', self._proc.pid)
            self._proc = None

    def _cli_auth_args(self):
        if self.cli_sasl_external:
            authc_args = [
                '-Y', 'EXTERNAL',
            ]
            if not self._log.isEnabledFor(logging.DEBUG):
                authc_args.append('-Q')
        else:
            authc_args = [
                '-x',
                '-D', self.root_dn,
                '-w', self.root_pw,
            ]
        return authc_args

    # no cover to avoid spurious coverage changes
    def _cli_popen(self, ldapcommand, extra_args=None, ldap_uri=None,
                   stdin_data=None):  # pragma: no cover
        if ldap_uri is None:
            ldap_uri = self.default_ldap_uri
        args = [
            ldapcommand,
            '-H', ldap_uri,
        ] + self._cli_auth_args() + (extra_args or [])
        self._log.debug('Run command: %r', ' '.join(args))
        proc = subprocess.Popen(
            args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self._log.debug('stdin_data=%r', stdin_data)
        stdout_data, stderr_data = proc.communicate(stdin_data)
        if stdout_data is not None:
            self._log.debug('stdout_data=%r', stdout_data)
        if stderr_data is not None:
            self._log.debug('stderr_data=%r', stderr_data)
        if proc.wait() != 0:
            raise RuntimeError(
                '{!r} process failed:\n{!r}\n{!r}'.format(
                    args, stdout_data, stderr_data
                )
            )
        return stdout_data, stderr_data

    def ldapwhoami(self, extra_args=None):
        """
        Runs ldapwhoami on this slapd instance
        """
        self._cli_popen(self.PATH_LDAPWHOAMI, extra_args=extra_args)

    def ldapadd(self, ldif, extra_args=None):
        """
        Runs ldapadd on this slapd instance, passing it the ldif content
        """
        self._cli_popen(self.PATH_LDAPADD, extra_args=extra_args,
                        stdin_data=ldif.encode('utf-8'))

    def ldapmodify(self, ldif, extra_args=None):
        """
        Runs ldapadd on this slapd instance, passing it the ldif content
        """
        self._cli_popen(self.PATH_LDAPMODIFY, extra_args=extra_args,
                        stdin_data=ldif.encode('utf-8'))

    def ldapdelete(self, dn, recursive=False, extra_args=None):
        """
        Runs ldapdelete on this slapd instance, deleting 'dn'
        """
        if extra_args is None:
            extra_args = []
        if recursive:
            extra_args.append('-r')
        extra_args.append(dn)
        self._cli_popen(self.PATH_LDAPDELETE, extra_args=extra_args)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()


class SlapdTestCase(unittest.TestCase):
    """
    test class which also clones or initializes a running slapd
    """

    server_class = SlapdObject
    server = None
    ldap_object_class = None

    def _open_ldap_conn(self, who=None, cred=None, **kwargs):
        """
        return a LDAPObject instance after simple bind
        """
        ldap_conn = self.ldap_object_class(self.server.ldap_uri, **kwargs)
        ldap_conn.protocol_version = 3
        #ldap_conn.set_option(ldap.OPT_REFERRALS, 0)
        ldap_conn.simple_bind_s(who or self.server.root_dn, cred or self.server.root_pw)
        return ldap_conn

    @classmethod
    def setUpClass(cls):
        cls.server = cls.server_class()
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()
