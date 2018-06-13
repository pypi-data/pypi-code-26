"""
Script to check the status of web pages and alert OpsGenie of an issue.
"""

from time import sleep
import requests
import click


@click.command()
@click.option('--count', default=1, type=int, help="The number of times to check the URL.")
@click.option('--wait', default=5, type=int, help="The number of seconds to wait between tries.")
@click.option('--timeout', default=10, type=int, help="The timeout in seconds.")
@click.argument('url')
def check(url, count, wait, timeout):
    """Checks the status of the given URL."""

    r = requests.get(url, timeout=timeout)

    i = 0
    while i < count:
        click.echo(r.status_code)
        i += 1
        sleep(wait)


__author__ = "Jordan Gregory <gregory.jordan.m@gmail.com"
__maintainer__ = "Jordan Gregory <gregory.jordan.m@gmail.com"
__version__ = "1.0.3"
__license__ = "MIT"
