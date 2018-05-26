import sys
import getpass
import click
import github
import forkedthanks.text as text


@click.command()
@click.argument('username', type=click.STRING)
def main(username):
    """Console script for forkedthanks."""
    print(text.newline())
    password = getpass.getpass(prompt='{}{}{}'.format(
        text.base_accent('Please enter a password for github account "'),
        text.base_accent2(username),
        text.base_accent('": '),
    ))
    if not password:
        print(text.notice_error('Password was empty 🤔'))
        return 1
    print(text.base('Connecting to Github...'))
    try:
        user = github.Github(username, password).get_user()
        all_repos = [repo for repo in user.get_repos()]
        forked_repos = [repo for repo in all_repos if repo.parent]
        starred_forked_repos = [
            repo for repo in forked_repos if user.has_in_starred(
                starred=repo.parent)
        ]
        starred_forked_repos_parents = [
            repo.parent for repo in starred_forked_repos
        ]
        print(text.newline(2))
        print(
            text.base('Repositories: ') +
            text.base_accent(len(starred_forked_repos)) +
            text.base(' starred out of ') +
            text.base_accent(len(forked_repos)) +
            text.base(' forks')
        )
        print(text.newline())
        for repo in forked_repos:
            element = (
                '{}' +
                text.base(' (') +
                text.base_accent2(repo.parent.full_name.split('/')[0]) +
                text.base(')')
            )
            if repo.parent in starred_forked_repos_parents:
                element = element.format(
                    text.base('\t⭐️\t') +
                    text.base_accent(repo.parent.name)
                )
            else:
                element = element.format(
                    text.base('\t\t') +
                    text.base_not_ok(repo.parent.name)
                )
            print(element)
        print(text.newline(2))
        if len(forked_repos) - len(starred_forked_repos) > 0:
            print(
                text.base('Staring ') +
                text.base_accent(
                    len(forked_repos) -
                    len(starred_forked_repos)
                ) +
                text.base(' repositories...')
            )
            for repo in forked_repos:
                if repo.parent not in starred_forked_repos_parents:
                    user.add_to_starred(repo.parent)
            print(text.newline(2))
            print(
                text.base_accent('✨ ❤️ ✨  Done! Thanks for sharing your love')
            )
            print(text.newline(2))
        else:
            print(
                text.base_accent(
                    '🙌  Everything\'s already starred, you\'re awesome!'
                )
            )
            print(text.newline(2))
        return 0
    except github.BadCredentialsException:
        print(text.notice_error('Wrong credentials 🤔'))
        return 1
    except (github.UnknownObjectException, github.BadUserAgentException,
            github.RateLimitExceededException, github.BadAttributeException,
            github.TwoFactorException):
        print(text.notice_error('Error communicating with Github 🤔'))
        return 1


if __name__ == "__main__":
    sys.exit(main())
