from yangsgoogle.credentials import CredentialManager
from yangsutil import LogUtil, StringUtil
from oauth2client import tools
import argparse

# const
SERVICE_NAME = ''
APP_NAME = ''
USER_NAME = ''
CLIENT_SECRET = 'client_secret.json'
CREDENTIAL_ROOT = '.credential'


def main():
    # object
    logger = LogUtil.get_logger(app_name='Google Credential Generator')

    ##############
    # arg parser #
    ##############
    arg = argparse.ArgumentParser(parents=[tools.argparser])

    arg.add_argument('-s', '--service_name')
    arg.add_argument('-a', '--app_name')
    arg.add_argument('-u', '--user_name')
    arg.add_argument('-c', '--client_secret')
    arg.add_argument('-d', '--credential_root')

    flags = arg.parse_args()
    flags.noauth_local_webserver = True

    # arg_dict
    arg_dict = dict()

    # service name
    arg_dict['service_name'] = flags.service_name if flags.service_name is not None else SERVICE_NAME
    arg_dict['app_name'] = flags.app_name if flags.app_name is not None else APP_NAME
    arg_dict['user_name'] = flags.user_name if flags.user_name is not None else USER_NAME
    arg_dict['client_secret'] = flags.client_secret if flags.client_secret is not None else CLIENT_SECRET
    arg_dict['credential_root'] = flags.credential_root if flags.credential_root is not None else CREDENTIAL_ROOT

    # validation
    for dict_key in arg_dict.keys():
        if StringUtil.is_none(arg_dict[dict_key]):
            logger.info('"%s" is none...' % dict_key)
            exit(1)

    # start
    CredentialManager(logger=logger).create(option=arg_dict, flags=flags)
