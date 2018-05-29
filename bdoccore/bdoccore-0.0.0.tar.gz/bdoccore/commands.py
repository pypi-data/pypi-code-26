
# -*- coding: utf-8 -*-
"""bdodatabase.core.commands"""


import shutil
import subprocess
import wget


class Command(object):
    """Basic command to be used on python script"""

    config_path = None
    action = None

    def __init__(self, logger, **kwargs):
        """Constructor for basic command to be used on python script

        Arguments:
            logger {logging.Logger} -- to log messages

        Raises:
            Exception -- Bad param 'logger'
            Exception -- Bad param 'action',
                available values are: [install, start]
        """
        if logger is None:
            raise Exception("Bad param 'logger'")
        self.logger = logger
        if kwargs.get('action') not in ['install', 'start']:
            raise Exception(
                ("Bad param 'action' available "
                 "values are: [install, start]"))
        self.action = kwargs.get('action')
        config_path = kwargs.get('config_path')
        if not config_path:
            raise Exception("Bad config_path provided")
        self.config_path = config_path

    def install(self):
        """Installation process"""
        raise NotImplementedError(
            'need to be overrided on inherit classes')

    def start(self):
        """Installation process"""
        raise NotImplementedError(
            'need to be overrided on inherit classes')

    def download(self, url, out_path):
        """
        Download file from 'url' to 'out_path'
         logging process start and end
        """
        self.logger.info('Downloading file: ...')
        self.logger.debug('  url={}'.format(url))
        self.logger.debug('  out_path={}'.format(out_path))
        wget.download(url, out=out_path)
        self.logger.info('Downloading file: DONE')

    def copy(self, src_file, dst_file):
        """Copy a file from source path to destination path"""
        self.logger.info('Copying file: ...')
        self.logger.debug('  src_file={}'.format(src_file))
        self.logger.debug('  dst_file={}'.format(dst_file))
        shutil.copy2(
            src_file,
            dst_file
        )
        self.logger.info('Copying file: DONE')

    def execute(self, cmd_args, shell=False):
        """Execute a command on OS terminal"""
        try:
            self.logger.info("Executing command : {}".format(
                cmd_args))
            return subprocess.call(cmd_args, shell=shell)
        except Exception as err:
            raise Exception(
                err, "Failed at handle command: {}".format(
                    cmd_args))
