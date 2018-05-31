# -*- coding: utf-8 -*-
import os

import click

from .flag_api import SubmitResult, GetinfoResult, FlagAPIHelper
from .capsule_api import (
    GetPublicKeyResult, DecodeResult, CapsuleAPIHelper
)


def get_api_endpoint():
    return os.getenv('THEMIS_FINALS_API_ENDPOINT')


@click.group()
def cli():
    pass


@cli.group(name='flag')
def flag_cli():
    pass


def print_request_exception(request, exception):
    click.echo(click.style(repr(exception), fg='red'))


def print_submit_results(results):
    click.echo('')
    for r in results:
        flag_part = click.style(r['flag'], bold=True)
        status_part = None
        if r['code'] == SubmitResult.SUCCESS:
            status_part = click.style(r['code'].name, fg='green')
        else:
            status_part = click.style(r['code'].name, fg='red')
        click.echo(flag_part + '  ' + status_part)


@flag_cli.command()
@click.argument('flags', nargs=-1)
def submit(flags):
    h = FlagAPIHelper(get_api_endpoint(),
                      exception_handler=print_request_exception)
    results = h.submit(*flags)
    print_submit_results(results)


def print_getinfo_results(results):
    click.echo('')
    for r in results:
        flag_part = click.style(r['flag'], bold=True)
        status_part = None
        extra_part = ''
        if r['code'] == GetinfoResult.SUCCESS:
            status_part = click.style(r['code'].name, fg='green')
            extra_part += click.style('\n  Team: ', bold=True, fg='yellow')
            extra_part += click.style(r['team'])
            extra_part += click.style('\n  Service: ', bold=True, fg='yellow')
            extra_part += click.style(r['service'])
            extra_part += click.style('\n  Round: ', bold=True, fg='yellow')
            extra_part += click.style('{0:d}'.format(r['round']))
            extra_part += click.style(
                '\n  Not before: ', bold=True, fg='yellow')
            extra_part += click.style(
                '{0:%-m}/{0:%-d} {0:%H}:{0:%M}:{0:%S}'.format(r['nbf']))
            extra_part += click.style('\n  Expires: ', bold=True, fg='yellow')
            extra_part += click.style(
                '{0:%-m}/{0:%-d} {0:%H}:{0:%M}:{0:%S}'.format(r['exp']))
        else:
            status_part = click.style(r['code'].name, fg='red')

        click.echo(flag_part + '  ' + status_part + extra_part)


@flag_cli.command()
@click.argument('flags', nargs=-1)
def getinfo(flags):
    h = FlagAPIHelper(get_api_endpoint(),
                      exception_handler=print_request_exception)
    results = h.getinfo(*flags)
    print_getinfo_results(results)


@cli.group(name='capsule')
def capsule_cli():
    pass


def print_public_key_result(result):
    click.echo('')
    if result['code'] == GetPublicKeyResult.SUCCESS:
        click.echo(click.style(result['code'].name, bold=True, fg='green'))
        click.echo(result['public_key'])
    else:
        click.echo(click.style(result['code'].name, bold=True, fg='red'))


@capsule_cli.command()
def public_key():
    h = CapsuleAPIHelper(get_api_endpoint())
    result = h.get_public_key()
    print_public_key_result(result)


def print_decode_result(result):
    print(result)
    click.echo('')
    if result['code'] == DecodeResult.SUCCESS:
        click.echo(click.style(result['code'].name, bold=True, fg='green'))
        if 'flag' in result['decoded']:
            click.echo(click.style('  Flag: ', bold=True, fg='yellow') +
                       result['decoded']['flag'])
    else:
        click.echo(click.style(result['code'].name, bold=True, fg='red'))


@capsule_cli.command()
@click.argument('capsule')
def decode(capsule):
    h = CapsuleAPIHelper(get_api_endpoint())
    result = h.decode(capsule)
    print_decode_result(result)
