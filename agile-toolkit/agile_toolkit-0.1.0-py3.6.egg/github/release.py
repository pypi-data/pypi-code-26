import click

from ..utils import command, niceJson
from ..repo import RepoManager


@click.command()
@click.pass_context
@click.option(
    '--yes', is_flag=True,
    help='Commit changes to github', default=False)
def release(ctx, yes):
    """Create a new release in github
    """
    with command():
        m = RepoManager(ctx.obj['agile'])
        branch = m.info['branch']
        if m.can_release('stage'):
            version = m.validate_version()
            name = 'v%s' % version
            body = ['Release %s from agiletoolkit' % name]
            api = m.github_repo()
            data = dict(
                tag_name=name,
                target_commitish=branch,
                name=name,
                body='\n\n'.join(body),
                draft=False,
                prerelease=False
            )
            if yes:
                data = m.wait(api.releases.create(data=data))
                m.message('Successfully created a new Github release')
            click.echo(niceJson(data))
        else:
            click.echo('skipped')
