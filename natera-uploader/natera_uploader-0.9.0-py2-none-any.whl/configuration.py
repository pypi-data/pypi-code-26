#!/usr/bin/env python

import argparse
import json
import os
from soyuz import __version__ as version
from utils import UploaderException


class Parameters(object):
    UPLOAD_ACTION = "upload"
    WES_SIGNATERA_UPLOAD = "wes_signatera"
    RAW_UPLOAD = "raw"
    CONFIG_ACTION = "config"
    GET_CONFIG = "get"
    SET_CONFIG = "set"
    VERSION_ACTION = "version"

    def __init__(self):
        parser = argparse.ArgumentParser(description="Constellation Sequencing Uploader v{}".format(version))

        parser.add_argument('--token', '-t', help='DNAnexus token with access to a single project with level UPLOAD')

        sp = parser.add_subparsers()

        # uploader upload
        upload_parser = sp.add_parser(Parameters.UPLOAD_ACTION, help='Upload sequencing folder')
        upload_parser.set_defaults(action=Parameters.UPLOAD_ACTION)

        sup = upload_parser.add_subparsers()

        # uploader upload raw
        raw_parser = sup.add_parser(Parameters.RAW_UPLOAD, help='Raw upload without any validation and modifications')
        raw_parser.set_defaults(upload_type=Parameters.RAW_UPLOAD)
        raw_parser.add_argument('folder', metavar='Folder')

        # uploader upload wes_signatera
        wes_signatera_parser = sup.add_parser(Parameters.WES_SIGNATERA_UPLOAD, help='Upload for WES Signatera')
        wes_signatera_parser.set_defaults(upload_type=Parameters.WES_SIGNATERA_UPLOAD)
        wes_signatera_parser.add_argument('folder', metavar='Folder')

        # uploader config
        config_parser = sp.add_parser(Parameters.CONFIG_ACTION,
                                      help='Configure uploader. This action updates ~/.uploader file')
        config_parser.set_defaults(action=Parameters.CONFIG_ACTION)

        scp = config_parser.add_subparsers()

        # uploader config get
        get_config_parser = scp.add_parser(Parameters.GET_CONFIG,
                                           help='Get uploader configuration')
        get_config_parser.set_defaults(config_action=Parameters.GET_CONFIG)
        get_config_parser.add_argument('config_parameter_key', metavar='Key')

        # uploader config set
        set_config_parser = scp.add_parser(Parameters.SET_CONFIG,
                                           help='Configure uploader. This action updates ~/.uploader file')
        set_config_parser.set_defaults(config_action=Parameters.SET_CONFIG)
        set_config_parser.add_argument('config_parameter_key', metavar='Key')
        set_config_parser.add_argument('config_parameter_value', metavar='Value')

        # uploader version
        version_parser = sp.add_parser(Parameters.VERSION_ACTION, help='Show version')
        version_parser.set_defaults(action=Parameters.VERSION_ACTION)

        self.__args = parser.parse_args()

        if self.__args.action == Parameters.VERSION_ACTION:
            print "v" + version
            quit(0)

    def get_token(self):
        return self.__args.token

    def get_folder(self):
        return self.__args.folder

    def get_action(self):
        return self.__args.action

    def get_upload_type(self):
        return self.__args.upload_type

    def get_config_action(self):
        return self.__args.config_action

    def get_config_parameter_key(self):
        return self.__args.config_parameter_key

    def get_config_parameter_value(self):
        return self.__args.config_parameter_value


class Settings(object):
    SETTING_FILE = ".uploader"

    def __init__(self, settings_base_path="~"):
        self.__settings = {}
        self.__full_path_to_settings = os.path.join(os.path.expanduser(settings_base_path), Settings.SETTING_FILE)

        if os.path.isfile(self.__full_path_to_settings):
            try:
                self.__settings = json.load(open(self.__full_path_to_settings))
            except Exception:
                raise UploaderException("{} is not a valid JSON".format(Settings.SETTING_FILE))

    def get_token(self):
        nexus = self.__get_dnanexus()
        if nexus and "token" in nexus:
            return str(nexus["token"])
        return None

    def set_token(self, token):
        self.__get_dnanexus()["token"] = token

    def get_base_dir(self):
        nexus = self.__get_dnanexus()
        if nexus and "basedir" in nexus:
            return str(nexus["basedir"])
        return "/data/seq"

    def set_basedir(self, basedir):
        self.__get_dnanexus()["basedir"] = basedir

    def dump(self):
        with open(self.__full_path_to_settings, 'wt') as out:
            json.dump(self.__settings, out, sort_keys=True, indent=4, separators=(',', ': '))

    def __get_dnanexus(self):
        if "dnanexus" not in self.__settings:
            self.__settings["dnanexus"] = {}
        return self.__settings["dnanexus"]
