import click

from ..repo import RepoManager


@click.command()
@click.pass_context
def validate(ctx):
    """Check if version of repository is semantic
    """
    m = RepoManager(ctx.obj['agile'])
    click.echo(m.validate_version())
