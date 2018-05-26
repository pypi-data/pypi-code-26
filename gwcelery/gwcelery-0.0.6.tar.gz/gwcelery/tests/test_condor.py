from unittest import mock

import pytest

from .. import app
from .. import condor


@pytest.mark.parametrize('subcommand,extra_args', [['rm', ()],
                                                   ['hold', ()],
                                                   ['release', ()],
                                                   ['q', ('-nobatch',)]])
@mock.patch('os.execvp', side_effect=SystemExit(0))
def test_condor_subcommand(mock_execvp, subcommand, extra_args):
    """Test all trivial Condor subcommands."""
    try:
        app.start(['gwcelery', 'condor', subcommand])
    except SystemExit as e:
        assert e.code == 0

    cmd = 'condor_' + subcommand
    mock_execvp.assert_called_once_with(
        cmd, (cmd,) + extra_args + condor.CONSTRAINTS)


@mock.patch('subprocess.check_output', return_value=b'<classads></classads>')
@mock.patch('os.execvp', side_effect=SystemExit(0))
def test_condor_submit_not_yet_running(mock_execvp, mock_check_output):
    """Test starting the Condor job."""
    try:
        app.start(['gwcelery', 'condor', 'submit'])
    except SystemExit as e:
        assert e.code == 0

    mock_check_output.assert_called_once_with(
        ('condor_q', '-xml') + condor.CONSTRAINTS)
    mock_execvp.assert_called_once_with(
        'condor_submit', ('condor_submit', condor.SUBMIT_FILE))


@mock.patch('subprocess.check_output',
            return_value=b'<classads><c></c></classads>')
@mock.patch('os.execvp', side_effect=SystemExit(0))
def test_condor_submit_already_running(mock_execvp, mock_check_output):
    """Test that we don't start the condor jobs if they are already running."""
    try:
        app.start(['gwcelery', 'condor', 'submit'])
    except SystemExit as e:
        assert e.code == 1

    mock_check_output.assert_called_once_with(
        ('condor_q', '-xml') + condor.CONSTRAINTS)
    mock_execvp.assert_not_called()
