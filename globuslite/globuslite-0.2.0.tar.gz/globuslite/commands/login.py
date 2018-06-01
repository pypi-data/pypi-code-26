import globus_sdk
import platform
from globuslite.config import (
    AUTH_RT_OPTNAME, TRANSFER_RT_OPTNAME,
    AUTH_AT_OPTNAME, TRANSFER_AT_OPTNAME,
    AUTH_AT_EXPIRES_OPTNAME, TRANSFER_AT_EXPIRES_OPTNAME,
    internal_auth_client, write_option, lookup_option,
    CLIENT_ID )


SCOPES = ('openid profile email', 
    'urn:globus:auth:scope:auth.globus.org:view_identity_set',
    'urn:globus:auth:scope:transfer.api.globus.org:all')

__all__ = ['login']

def exchange_code_and_store_config( native_client, auth_code ):
    tkn = native_client.oauth2_exchange_code_for_tokens( auth_code )
    tkn = tkn.by_resource_server

    # extract access tokens from final response
    transfer_at = (
        tkn['transfer.api.globus.org']['access_token'])
    transfer_at_expires = (
        tkn['transfer.api.globus.org']['expires_at_seconds'])
    transfer_rt = (
        tkn['transfer.api.globus.org']['refresh_token'])
    auth_at = (
        tkn['auth.globus.org']['access_token'])
    auth_at_expires = (
        tkn['auth.globus.org']['expires_at_seconds'])
    auth_rt = (
        tkn['auth.globus.org']['refresh_token'])

    # revoke any existing tokens
    for token_opt in (TRANSFER_RT_OPTNAME, TRANSFER_AT_OPTNAME,
                      AUTH_RT_OPTNAME, AUTH_AT_OPTNAME):
        token = lookup_option(token_opt)
        if token:
            native_client.oauth2_revoke_token(token)

    # write new tokens to config
    write_option(TRANSFER_RT_OPTNAME, transfer_rt)
    write_option(TRANSFER_AT_OPTNAME, transfer_at)
    write_option(TRANSFER_AT_EXPIRES_OPTNAME, transfer_at_expires)
    write_option(AUTH_RT_OPTNAME, auth_rt)
    write_option(AUTH_AT_OPTNAME, auth_at)
    write_option(AUTH_AT_EXPIRES_OPTNAME, auth_at_expires)

def do_link_login_flow():
    """
    Prompt the user to visit a URL to retrieve an access code.
    """

    client = globus_sdk.NativeAppAuthClient( CLIENT_ID )
    label = platform.node()
    client.oauth2_start_flow( refresh_tokens=True, 
        prefill_named_grant=label,
        requested_scopes=SCOPES )

    authorize_url = client.oauth2_get_authorize_url()
    print('Go to this URL and login: {}'.format( authorize_url ) )

    get_input = getattr(__builtins__, 'raw_input', input)
    auth_code = get_input(
        'Enter code you get after login here: ').strip()

    exchange_code_and_store_config( client, auth_code )

def login( *args, **kwargs ):
    """
    Log into Globus services to authorize this application.
    """

    do_link_login_flow( *args, **kwargs )

