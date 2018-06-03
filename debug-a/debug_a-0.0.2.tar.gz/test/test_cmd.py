# coding: utf-8


import click
from debug_a.utils import create_logger

log_file = "test.log"
logger = create_logger('clg', log_file=log_file)


@click.group()
def da():
    print('da')


@da.command()
def cl():
    logger = create_logger('cl', log_file=log_file)
    logger.info("test running")


@da.command()
def clg():
    logger.info("test running")


if __name__ == "__main__":
    da()
