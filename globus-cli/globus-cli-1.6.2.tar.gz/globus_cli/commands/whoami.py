import click

from globus_sdk.exc import AuthAPIError

from globus_cli.safeio import safeprint, formatted_print, FORMAT_TEXT_RECORD
from globus_cli.parsing import common_options
from globus_cli.helpers import is_verbose
from globus_cli.services.auth import get_auth_client


@click.command('whoami',
               help=('Show the currently logged-in identity.'))
@common_options(no_map_http_status_option=True)
@click.option("--linked-identities", is_flag=True,
              help=("Also show identities linked to the currently logged-in "
                    "identity."))
def whoami_command(linked_identities):
    """
    Executor for `globus whoami`
    """
    client = get_auth_client()

    # get userinfo from auth.
    # if we get back an error the user likely needs to log in again
    try:
        res = client.oauth2_userinfo()
    except AuthAPIError:
        safeprint('Unable to get user information. Please try '
                  'logging in again.', write_to_stderr=True)
        click.get_current_context().exit(1)

    # --linked-identities either displays all usernames or a table if verbose
    if linked_identities:
        try:
            formatted_print(
                res["identity_set"],
                fields=[("Username", "username"), ("Name", "name"),
                        ("ID", "sub"), ("Email", "email")],
                simple_text=(None if is_verbose() else "\n".join(
                    [x["username"] for x in res["identity_set"]])))
        except KeyError:
            safeprint("Your current login does not have the consents required "
                      "to view your full identity set. Please log in again "
                      "to agree to the required consents.",
                      write_to_stderr=True)

    # Default output is the top level data
    else:
        formatted_print(
            res, text_format=FORMAT_TEXT_RECORD,
            fields=[("Username", "preferred_username"), ("Name", "name"),
                    ("ID", "sub"), ("Email", "email")],
            simple_text=(None if is_verbose() else res["preferred_username"]))
