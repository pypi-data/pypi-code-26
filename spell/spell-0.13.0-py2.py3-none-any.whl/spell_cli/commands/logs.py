# -*- coding: utf-8 -*-
import click

from api_client.runs_client import RunsClient
from spell_cli.exceptions import (
    ExitException,
    api_client_exception_handler,
)
from spell_cli.log import logger
from spell_cli.utils import convert_to_local_time


@click.command(name="logs",
               short_help="Retrieve logs for a run")
@click.argument("run_id")
@click.option("-f", "--follow", is_flag=True,
              help="Follow log output")
@click.option("-n", "--tail", default=0,
              help="Show the last NUM lines")
@click.option("-v", "--verbose", is_flag=True,
              help="Print additional information")
@click.pass_context
def logs(ctx, run_id, follow, tail, verbose, stop_status=None):
    """
    Retrieve logs for a run specified by RUN_ID.

    Streams logs for the specified run. For runs with a large number of log lines
    the `--tail N` option allows the user to print only the last N lines. When
    following with `--follow` use `Ctrl + C` to detach.
    """
    # grab the logs from the API
    token = ctx.obj["config_handler"].config.token
    run_client = RunsClient(token=token, **ctx.obj["client_args"])
    with api_client_exception_handler():
        logger.info("Retrieving run logs from Spell")
        try:
            for entry in run_client.get_run_log_entries(run_id, follow=follow, offset=-tail):
                pretty_print_log_entry(entry, verbose)
                if entry.get("status_event"):
                    status = entry.get("status", "")
                    if stop_status is not None and status == stop_status:
                        break
            if stop_status is not None and status != stop_status:
                raise ExitException("Run ended before entering the {} state".format(stop_status))
        except KeyboardInterrupt:
            if stop_status is not None:
                raise click.Abort()

            click.echo()
            click.echo(u"✨ Use 'spell logs {}' to view logs again".format(run_id))


def pretty_print_log_entry(entry, verbose=False):
    message = entry.get("log", "")

    if entry.get("status_event"):
        message = u"✨ " + message
    elif verbose:
        try:
            timestamp = convert_to_local_time(entry.get("@timestamp"))
        except Exception:
            logger.info("Fail to parse @timestamp")
            timestamp = entry.get("@timestamp", "<missing timestamp>")
        status = entry.get("status", "<missing status>")
        prefix = "{timestamp}: {status}:".format(status=status, timestamp=timestamp)
        if isinstance(message, str):
            message = message.replace("\r", "\r {prefix} ".format(prefix=prefix))
        message = u"{prefix} {message}".format(message=message, prefix=prefix)

    click.echo(message)
