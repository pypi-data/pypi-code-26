# -*- coding: utf-8 -*-

# Copyright 2018 Spotify AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import asyncio
import logging
import re
import sys
import tempfile

import click
import ulogger

from scanctl import github
from scanctl import whitesource


loop = asyncio.get_event_loop()


@click.group()
@click.option('-v', '--verbose', count=True)
@click.pass_context
def main(ctx, verbose):
    ctx.obj = {}
    if verbose > 2:
        verbose = 2
    levels = {0: 'WARNING', 1: 'INFO', 2: 'DEBUG'}
    level = levels.get(verbose, 0)
    ulogger.setup_logging('scanctl', level, ['stream'])


# github api commands

@main.group(name='github')
@click.option('--url', default='https://api.github.com/v3')
@click.option('--token', required=True,
              help='Token to use for GitHub API access.')
@click.pass_context
def github_cmd(ctx, url, token):
    ctx.obj['gh'] = github.ApiClient(url, token)


@github_cmd.command(name='list-orgs')
@click.pass_context
def github_list_orgs(ctx):
    gh = ctx.obj['gh']
    for org in gh.orgs():
        print(org.login)


@github_cmd.command(name='list-repos')
@click.argument('orgs', nargs=-1)
@click.pass_context
def github_list_repos(ctx, orgs):
    gh = ctx.obj['gh']
    if not orgs:
        orgs = (org.login for org in gh.orgs())
    for org in orgs:
        for repo in gh.repos(org):
            print(repo.full_name)


# whitesource api commands

@main.group(name='whitesource')
@click.option('--url', default='https://saas.whitesourcesoftware.com/api')
@click.option('--token', required=True,
              help='Token to use for Whitesource API access.')
@click.pass_context
def ws_cmd(ctx, url, token):
    ctx.obj['ws'] = whitesource.ApiClient(url, token)


@ws_cmd.command(name='list-products')
@click.pass_context
def ws_list_products(ctx):
    ws = ctx.obj['ws']
    for product in ws.products():
        print(product)


@ws_cmd.command(name='delete-products')
@click.pass_context
def ws_delete_products(ctx):
    ws = ctx.obj['ws']
    for product in ws.products():
        product.delete()


@ws_cmd.command(name='list-projects')
@click.argument('products', nargs=-1)
@click.pass_context
def ws_list_projects(ctx, products):
    ws = ctx.obj['ws']
    products = frozenset(products)
    for product in ws.products():
        if products and product.name not in products:
            continue
        for project in product.projects():
            print(product, project)


@ws_cmd.command(name='delete-projects')
@click.argument('products', nargs=-1)
@click.pass_context
def ws_delete_projects(ctx, products):
    ws = ctx.obj['ws']
    products = frozenset(products)
    for product in ws.products():
        if products and product.name not in products:
            continue
        for project in product.projects():
            project.delete()


# fs-agent commands

@main.command()
@click.argument('repositories', nargs=-1)
@click.option('--file', '-f', type=click.File(),
              help='Path to file containing a list of repositories to scan.')
@click.option('--remote', default='github.com')
@click.option('--url', default='https://saas.whitesourcesoftware.com/api')
@click.option('--token', required=True,
              help='Token to use for Whitesource API access.')
@click.option('--limit', type=click.INT, default=16,
              help='Maximum number of concurrent tasks while scanning.')
def scan(repositories, file, remote, url, token, limit):
    if not (repositories or file):
        sys.exit('No repositories to scan.')
    if limit <= 0:
        sys.exit('Task limit cannot be less than 1.')

    sem = asyncio.Semaphore(limit)
    agent = whitesource.FsAgent(token=token)
    if file:
        repositories = list(repositories)
        repositories.extend(file.read().splitlines())
    repositories = frozenset(repositories)

    tasks = []
    for repository in repositories:
        ssh_url = f'git@{remote}:{repository}.git'
        coro = bounded(sem, _clone_and_scan(ssh_url, agent))
        task = loop.create_task(coro)
        tasks.append(task)

    fut = asyncio.gather(*tasks)
    loop.run_until_complete(fut)


async def bounded(sem, coro):
    async with sem:
        return await coro


async def _clone_and_scan(ssh_url, agent):
    tmp = tempfile.TemporaryDirectory()
    try:
        org, repo = _parse_ssh_url(ssh_url)
        click.echo(f'{org}/{repo}: ' + click.style('clone', fg='blue'))
        await github.clone(ssh_url, tmp.name)
        click.echo(f'{org}/{repo}: ' + click.style('scan', fg='blue'))
        await agent.run(org, repo, tmp.name)
        click.echo(f'{org}/{repo}: ' + click.style('complete', fg='green'))
    except Exception as e:
        logging.debug(f'{org}/{repo}: {e}')
        click.echo(f'{org}/{repo}: ' + click.style('failed', fg='red'))


def _parse_ssh_url(ssh_url):
    patt = 'git@[^:]+:(?P<org>[^/]+)/(?P<repo>.+).git'
    m = re.match(patt, ssh_url)
    if not m:
        logging.info(f'ssh_url failed to match: {ssh_url}')
        return
    return m.group('org'), m.group('repo')
