from asyncio import gather

import click

from ..api import GithubApi
from .utils import get_repos
from ..utils import wait


@click.command()
@click.pass_context
@click.option(
    '--list', is_flag=True,
    help='list open milestones', default=False)
@click.option('--close', help='milestone to close', default='')
def milestones(ctx, list, close):
    """View/edit/close milestones on github
    """
    repos = get_repos(ctx.parent.agile.get('labels'))
    if list:
        wait(_list_milestones(repos))
    elif close:
        click.echo('Closing milestones "%s"' % close)
        wait(_close_milestone(repos, close))
    else:
        click.echo(ctx.get_help())


async def _list_milestones(repos):
    git = GithubApi()
    requests = []
    for repo in repos:
        repo = git.repo(repo)
        requests.append(repo.milestones.get_list())
    data = await gather(*requests)
    milestones = set()
    for repo in data:
        milestones.update((data['title'] for data in repo))
    for title in sorted(milestones):
        click.echo(title)


def _close_milestone(repos, milestone):
    git = GithubApi()
    requests = []
    for repo in repos:
        repo = git.repo(repo)
        requests.append(_close_repo_milestone(repo, milestone))
    return gather(*requests)


async def _close_repo_milestone(repo, milestone):
    milestones = await repo.milestones.get_list()
    for m in milestones:
        if m['title'] == milestone:
            await repo.milestones.update(m, {'state': 'closed'})
            click.echo('Closed milestone %s' % m['html_url'])
