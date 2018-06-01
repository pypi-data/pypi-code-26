"""
The methods in this file handle building various authorization objets
and other various operations related to authorization.
"""

import re
from globus_sdk import AuthClient, RefreshTokenAuthorizer
from globuslite.config import (set_auth_access_token, get_auth_tokens,
                               internal_auth_client, 
                               get_transfer_tokens, )
from globuslite.version import app_name

_UUID_REGEX = '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'

def is_valid_uuid(identity_name):
    """
    Check if a string is a valid uuid.
    Does not do any preprocessing of the identity name, so you must do so
    before invocation.
    """
    if re.match(_UUID_REGEX, identity_name) is None:
        return False
    else:
        return True

def verify_uuid( id_name ):
    '''
    Throw an exception if id_name is not valid. Else, return id_name
    unchanged.
    '''

    if is_valid_uuid( id_name ):
        return id_name
    else:
        raise RuntimeError('Invalid Globus identifier.')

def _update_access_tokens( token_response ):
    tokens = token_response.by_resource_server['auth.globus.org']
    set_auth_access_token( tokens['access_token'], 
                           tokens['expires_at_seconds'])

def get_refresh_authorizer( tokens ):
    """
    Retrieve a refresh token authorizer from the configuration file.
    """

    authorizer = None

    if tokens['refresh_token'] is not None:
        authorizer = RefreshTokenAuthorizer(
            tokens['refresh_token'], internal_auth_client(),
            tokens['access_token'], int(tokens['access_token_expires']),
            on_refresh=_update_access_tokens)
    else:
        raise RuntimeError('No refresh token found. Please login first.')
   
    return authorizer

def get_auth_client():
    """
    Retrieve an authorization client.
    """

    authorizer = get_refresh_authorizer()
    client = AuthClient( authorizer = authorizer, app_name=app_name )
    
    return client

