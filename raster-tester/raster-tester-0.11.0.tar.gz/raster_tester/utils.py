
import click


def exception_raiser(message, no_stderr):
    if no_stderr:
        click.echo("not ok - %s" % (message))
    else:
        raise click.ClickException("not ok - {}".format(message))
