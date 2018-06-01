import click

from mongoladdu import logger
from mongoladdu.migrations import MongoLaddu


@click.group()
@click.argument('env')
@click.pass_context
def cli(ctx, env):
    logger.init("mongoladdu.migrations")
    ctx.obj = MongoLaddu(env)


@cli.command()
@click.pass_obj
def run(ctx):
    ctx.run()


if __name__ == '__main__':
    cli()