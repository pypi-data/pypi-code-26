import click


@click.command()
def cli():
    """Example script."""
    file_object = open('../../data/data.txt', 'r')
    for line in file_object:
        click.echo(line)
    file_object.close()
    click.echo('Hello World!')
