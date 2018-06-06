# Driver superclass to implement common SFTP-based deployment functions

import os
import subprocess
import logging
_logging = logging.getLogger(__name__)

from wordpress_cd.drivers import driver
from wordpress_cd.drivers.base import BaseDriver


@driver('sftp')
class SFTPHostDriver(BaseDriver):
    def __str__(self):
        return "SFTP"

    def __init__(self, args):
        _logging.debug("Initialising SFTP Host Driver")
        super(SFTPHostDriver, self).__init__(args)

        self.sftp_host = os.getenv('SFTP_HOST')
        self.sftp_port = os.getenv('SFTP_PORT')
        self.sftp_user = os.getenv('SFTP_USER')
        self.sftp_pass = os.getenv('SFTP_PASS')
        self.sftp_path = os.getenv('SFTP_PATH')

    def _deploy_module(self, type):
        _logging.info("Deploying of '{0}' {1} branch '{2}' to host '{3}' (job id: {4})...".format(module_id, type, self.git_branch, self.sftp_host, self.job_id))

        # Sync new site into place, leaving config/content in place
        pluginroot = "{0}/wp-content/{1}s/{2}".format(self.sftp_path, type, module_id)
        deployargs = [
            "rsync", "-r",
            "-e", self._get_rsync_rsh(),
            "--exclude=.git*",
            "--delete",
            ".", "{0}@{1}:{2}".format(self.sftp_user, self.sftp_host, pluginroot)
        ]
        exitcode = subprocess.call(deployargs)
        _logging.debug("rsync exitcode: {0}".format(exitcode))
        if exitcode != 0:
            logging.error("Unable to sync new copy of plugin into place. Exit code: {0}".format(exitcode))
            return exitcode

        # Done
        _logging.info("Deployment of '{0}' {1} branch '{2}' to host '{3}' successful (job id: {4})...".format(module_id, type, self.git_branch, self.sftp_host, self.job_id))
        return 0

    def deploy_site(self):
        _logging.info("Deploying branch '{0}' to  host '{1}' (job id: {2})...".format(self.git_branch, self.sftp_host, self.job_id))

        # Sync new site into place, leaving config/content in place
        os.chdir("build/wordpress")
        deployargs = [
            "sftp", "-r",
        ]
        if self.sftp_port is not None:
            deployargs.extend(['-P', self.sftp_port])
        # [TODO] Find a way to pass the password through (!)
        #if self.sftp_pass is not None:
        #    deployargs.extend(['--password={0}'.format(self.sftp_pass)])
        deployargs.extend([
            "{0}@{1}:{2}".format(self.sftp_user, self.sftp_host, self.sftp_path)
        ])
        print deployargs
        deployenv = os.environ.copy()
        deployproc = subprocess.Popen(deployargs, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=deployenv)
        stdout, stderr = deployproc.communicate(self.sftp_pass)
        print "STDOUT: " + stdout
        print "STDERR: " + stderr
        deployproc.wait()
        exitcode = deployproc.returncode
        _logging.debug("rsync exitcode: {0}".format(exitcode))
        if exitcode != 0:
            logging.error("Unable to sync new site into place. Exit code: {0}".format(exitcode))
            print deployproc.stderr.read()
            return exitcode

        # Done
        _logging.info("Deployment of branch '{0}' to  host '{1}' successful (job id: {2})...".format(self.git_branch, self.sftp_host, self.job_id))
        return 0
