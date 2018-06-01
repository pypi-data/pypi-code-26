import click
import os


@click.command()
def cli():
    """Example script."""
    foo_config = open(
        os.path.join(os.path.dirname(__file__), "../data/data.txt")
    ).read()
    click.echo(foo_config)

    # file_object = open('../data/data.txt', 'r')
    # for line in file_object:
    #     click.echo(line)
    # file_object.close()
    click.echo('Hello World!')
