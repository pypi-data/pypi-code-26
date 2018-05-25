import configparser
import pathlib

import click

repositories = [
    {
        'name': 'pypi',
        'url': 'https://pypi.org/simple',
        'trusted-host': 'pypi.org'
    },
    {
        'name': 'douban',
        'url': 'https://pypi.douban.com/simple',
        'trusted-host': 'pypi.douban.com'
    },
    {
        'name': 'tencent',
        'url': 'https://mirrors.cloud.tencent.com/pypi/simple',
        'trusted-host': 'mirrors.cloud.tencent.com'
    },
    {
        'name': 'aliyun',
        'url': 'https://mirrors.aliyun.com/pypi/simple/',
        'trusted-host': 'mirrors.aliyun.com'
    },
]

pip = pathlib.Path.home() / pathlib.Path('.pip')


@click.group()
def cli():
    pass


@click.command()
@click.argument('repository')
def use(repository: str):
    for one in repositories:
        if one['name'] == repository:
            print(f'Setting to {repository}')
            config = configparser.ConfigParser()
            config['global'] = {'index-url':one['url'], 'trusted-host':one['trusted-host']}
            if not pip.exists():
                pip.mkdir()
            with open(pip.as_posix() + 'pip.conf','w') as file:
                config.write(file)
            return
    else:
        print(f'No repository {repository}')


@click.command()
def list():
    for repository in repositories:
        print(f'{repository["name"]:20}{repository["url"]}\n')

@click.command()
def show():
    if pip.exists():
        config = configparser.ConfigParser()
        config.read(pip.as_posix() + 'pip.conf')
        print(f'Current: {config["global"]["index-url"]}')
    else:
        print('{:20}{}'.format(repositories[0]['name'], repositories[0]['url']))

def main():
    cli.add_command(list)
    cli.add_command(use)
    cli.add_command(show)
    cli()

if __name__ == '__main__':
    main()
