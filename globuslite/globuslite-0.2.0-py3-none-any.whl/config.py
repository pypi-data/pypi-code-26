"""
The methods in this file handle interacting with the configuration 
file which stores information like authorization tokens.
"""

import yaml
from configobj import ConfigObj
from globuslite import version
import os
import globus_sdk

CONFIG_FILE = '~/.globuslite.ini'
CONFIG_PATH = os.path.expanduser( CONFIG_FILE )
AUTH_RT_OPTNAME = 'auth_refresh_token'
AUTH_AT_OPTNAME = 'auth_access_token'
AUTH_AT_EXPIRES_OPTNAME = 'auth_access_token_expires'
TRANSFER_RT_OPTNAME = 'transfer_refresh_token'
TRANSFER_AT_OPTNAME = 'transfer_access_token'
TRANSFER_AT_EXPIRES_OPTNAME = 'transfer_access_token_expires'

CLIENT_ID = '257aa35a-4619-4806-80eb-e8751380a206'

def get_config_obj():
    conf = ConfigObj( CONFIG_PATH )
    return conf

def lookup_option( option ):
    '''
    Retrieve the value of some option in the configuration file.

    Args:
        option: key to lookup
    '''
    conf = get_config_obj()
    try:
        return conf[option]
    except KeyError:
        return None

def write_option( opt, val ):
    '''
    Set opt to value of val in configuration file.
    '''

    # Deny rwx to group and world.
    old_umask = os.umask(0o077)
    config = get_config_obj()
    config[opt] = val
    config.write()
    os.umask( old_umask )

def get_auth_tokens():
    '''
    Retrieve authorization tokens from configuration file.
    '''

    return {
        'refresh_token': lookup_option(AUTH_RT_OPTNAME) , 
        'access_token': lookup_option(AUTH_AT_OPTNAME),
        'access_token_expires': lookup_option(AUTH_AT_EXPIRES_OPTNAME)
    }

def get_transfer_tokens():
    '''
    Retrieve trasfer tokens from configuration file.
    '''

    return {
        'refresh_token': lookup_option( TRANSFER_RT_OPTNAME ),
        'access_token': lookup_option( TRANSFER_AT_OPTNAME ),
        'access_token_expires': lookup_option( TRANSFER_AT_EXPIRES_OPTNAME )
    }

def set_auth_access_token( token, expires_at ):
    '''
    Set the authorization access tokens in configuration file.
    '''
    write_option( AUTH_AT_OPTNAME, token)
    write_option( AUTH_AT_EXPIRES_OPTNAME, expires_at )

def internal_auth_client():
    return globus_sdk.NativeAppAuthClient( CLIENT_ID, app_name = version.app_name )
