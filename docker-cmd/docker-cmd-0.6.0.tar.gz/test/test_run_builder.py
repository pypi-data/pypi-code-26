import pytest
from docker_cmd.builder import DockerRunBuilder


cmds = [
    ('foo bar', 'docker run test foo bar'),
    ('bash -c "foo bar"', 'docker run test bash -c "foo bar"'),
    ('bash -c "foo bar \"foz baz\""', 'docker run test bash -c "foo bar \"foz baz\""'),
]


@pytest.mark.parametrize("command,expected", cmds)
def test_run(command, expected):
    assert expected == DockerRunBuilder('test').build(command)


def test_remove():
    assert 'docker run --rm test cmd' == DockerRunBuilder('test').auto_remove().build('cmd')


def test_volumes():
    assert 'docker run -v h:m -v h2:m2 test cmd' \
           == DockerRunBuilder('test').volume('h', 'm').volume('h2', 'm2').build('cmd')


def test_volume_read_only():
    assert 'docker run -v h:m:ro test cmd' == \
           DockerRunBuilder('test').volume('h', 'm', True).build('cmd')


def test_environments():
    assert 'docker run -e k=v -e k2=v2 test cmd' == \
           DockerRunBuilder('test').environment('k', 'v').environment('k2', 'v2').build('cmd')


def test_passed_environments():
    assert 'docker run -e BAR test cmd' == \
           DockerRunBuilder('test').pass_environment('BAR').build('cmd')


def test_bash():
    assert 'docker run test bash -c "cmd"' == \
           DockerRunBuilder('test').in_bash().build('cmd')


def test_bash_escaped():
    assert 'docker run test bash -c "cmd \"foo bar\""' == \
           DockerRunBuilder('test').in_bash().build('cmd "foo bar"')

