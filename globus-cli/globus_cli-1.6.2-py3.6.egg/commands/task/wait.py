import click

from globus_cli.parsing import (
    common_options, task_id_arg, synchronous_task_wait_options)

from globus_cli.services.transfer import task_wait_with_io


@click.command('wait', help='Wait for a task to complete')
@common_options
@task_id_arg
@synchronous_task_wait_options
def task_wait(meow, heartbeat, polling_interval, timeout, task_id):
    """
    Executor for `globus task wait`
    """
    task_wait_with_io(meow, heartbeat, polling_interval, timeout, task_id)
