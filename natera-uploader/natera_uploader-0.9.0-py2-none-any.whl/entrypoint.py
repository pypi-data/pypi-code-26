#!/usr/bin/env python

from dx import DxContext
from dx import WesSignateraDxUploader, RawDxUploader
from configuration import Parameters
from configuration import Settings
from data import WesSignateraSeqFolder, RawSeqFolder
from utils import UploaderException


def main():
    try:
        params = Parameters()
        settings = Settings()
        if params.get_action() == Parameters.UPLOAD_ACTION:

            token = params.get_token()
            if not token:
                token = settings.get_token()
            if not token:
                raise UploaderException("Token was not specified")

            if params.get_upload_type() == Parameters.WES_SIGNATERA_UPLOAD:
                uploader = WesSignateraDxUploader(DxContext(token), settings.get_base_dir())
                folder = WesSignateraSeqFolder(params.get_folder())

                if not folder.is_valid():
                    raise UploaderException("Data folder is not in a valid state")

                uploader.upload(folder)

            elif params.get_upload_type() == Parameters.RAW_UPLOAD:
                uploader = RawDxUploader(DxContext(token), settings.get_base_dir())
                folder = RawSeqFolder(params.get_folder())

                if not folder.is_valid():
                    raise UploaderException("Data folder is not in a valid state")

                uploader.upload(folder)

        elif params.get_action() == Parameters.CONFIG_ACTION:

            if params.get_config_action() == Parameters.GET_CONFIG:
                if params.get_config_parameter_key() == "token":
                    print settings.get_token()
                elif params.get_config_parameter_key() == "basedir":
                    print settings.get_base_dir()

            elif params.get_config_action() == Parameters.SET_CONFIG:
                if params.get_config_parameter_key() == "token":
                    settings.set_token(params.get_config_parameter_value())
                elif params.get_config_parameter_key() == "basedir":
                    settings.set_basedir(params.get_config_parameter_value())
                else:
                    raise UploaderException("There is no parameter '{}'".format(params.get_config_parameter_key()))
                settings.dump()
                print "Set {} to {}".format(params.get_config_parameter_key(), params.get_config_parameter_value())

    except UploaderException as e:
        print str(e)
        quit(1)


if __name__ == "__main__":
    main()
