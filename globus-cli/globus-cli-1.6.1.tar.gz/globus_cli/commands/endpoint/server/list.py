import click

from globus_cli.parsing import common_options, endpoint_id_arg
from globus_cli.safeio import (
    formatted_print, FORMAT_TEXT_RECORD, FORMAT_TEXT_TABLE)
from globus_cli.services.transfer import get_endpoint_w_server_list


@click.command('list', help='List all servers belonging to an endpoint')
@common_options
@endpoint_id_arg
def server_list(endpoint_id):
    """
    Executor for `globus endpoint server list`
    """
    # raises usage error on shares for us
    endpoint, server_list = get_endpoint_w_server_list(endpoint_id)

    if server_list == 'S3':  # not GCS -- this is an S3 endpoint
        server_list = {'s3_url': endpoint['s3_url']}
        fields = [("S3 URL", 's3_url')]
        text_format = FORMAT_TEXT_RECORD
    else:  # regular GCS host endpoint
        fields = (('ID', 'id'),
                  ('URI', lambda s: (s['uri'] or
                                     "none (Globus Connect Personal)")))
        text_format = FORMAT_TEXT_TABLE
    formatted_print(server_list, text_format=text_format, fields=fields)
