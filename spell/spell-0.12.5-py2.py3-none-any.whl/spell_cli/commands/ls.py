# -*- coding: utf-8 -*-
import click

from api_client.resources_client import ResourcesClient
from spell_cli.exceptions import api_client_exception_handler
from spell_cli.log import logger
from spell_cli.utils import (
    prettify_size,
    convert_to_local_time,
    truncate_string,
)


# display order of columns
COLUMNS = [
    "size",
    "date",
    "path",
]


@click.command(name="ls",
               short_help="List resource files")
@click.argument("path", default="")
@click.option("-h", "human_readable", help="Display file sizes in human-readable format",
              is_flag=True, default=False)
@click.pass_context
def ls(ctx, path, human_readable):
    """
    List resource files for datasets, run outputs, and uploads.

    Resources are the generic name for datasets, models, or any other files that
    can be made available to a run. Spell keeps these organized for you in a
    remote filesystem that is browsable with the `ls` command, with the resources
    placed into directories that reflect their origin.

    There are many ways resources are generated. The user can upload resources
    directly with `spell upload` or execute a run with `spell run` that writes
    files to disk. Spell also provides a number of publicly-accessible datasets.
    """
    # grab the ls from the API
    token = ctx.obj["config_handler"].config.token
    r_client = ResourcesClient(token=token, **ctx.obj["client_args"])

    def format_ls_lines(ls):
        for ls_line in ls:
            if ls_line.date:
                ls_line.date = convert_to_local_time(ls_line.date, include_seconds=False)
            else:
                ls_line.date = "-"

            if ls_line.size is None:
                ls_line.size = "-"
            elif human_readable:
                ls_line.size = prettify_size(ls_line.size)

            status_suffix = ""
            if ls_line.upload_status is not None:
                if ls_line.upload_status == "initialized":
                    status_suffix = " (uploading)"
                elif ls_line.upload_status == "upload_complete":
                    status_suffix = " (pending)"
                elif ls_line.upload_status == "failed":
                    status_suffix = " (failed)"

            ls_line.date = truncate_string(ls_line.date, 14, fixed_width=True)
            ls_line.size = truncate_string(ls_line.size, 8, fixed_width=True)
            ls_line.path = truncate_string(ls_line.path, 60-len(status_suffix), fixed_width=True) + status_suffix
            yield ls_line

    found_a_line = False
    with api_client_exception_handler():
        logger.info("Retrieving resource list from Spell")
        ls = format_ls_lines(r_client.get_ls(path))
        for l in ls:
            click.echo(" ".join([l.size, l.date, l.path]))
            found_a_line = True

    if not found_a_line:
        click.echo("No files for path {}".format(path), err=True)
        return
