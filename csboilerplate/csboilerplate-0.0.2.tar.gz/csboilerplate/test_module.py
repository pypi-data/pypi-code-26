import argparse
import logging
import pytest
import signal
import sys
from unittest.mock import patch, Mock

import csboilerplate


# missing: test SIGTERM handling, dunno how to mock that


def noop(app):
    pass


@pytest.fixture(autouse=True)
def reset_sigterm_handler():
    signal.signal(signal.SIGTERM, signal.SIG_DFL)


def test_export():
    assert 'cli_app' in dir(csboilerplate)
    assert 'CommandLineApp' in dir(csboilerplate)


def test_cli_app():
    decorator = csboilerplate.cli_app()
    assert callable(decorator)
    App = decorator(noop)
    assert isinstance(App, csboilerplate.CommandLineApp)


@patch('csboilerplate.CommandLineApp')
def test_cli_app_kwargs(patched):
    decorator = csboilerplate.cli_app(a='a', b='b')
    decorator(noop)
    patched.assert_called_once()
    patched.assert_called_once_with(noop, a='a', b='b')


def test_CommandLineApp():
    dummy_main = Mock()
    App = csboilerplate.CommandLineApp(dummy_main)
    assert callable(App)
    dummy_main.assert_not_called()
    with pytest.raises(SystemExit):
        App()
    dummy_main.assert_called_once_with(App)


def test_CommandLineApp_argparser():
    App = csboilerplate.CommandLineApp(noop)
    assert isinstance(App.argparser, argparse.ArgumentParser)
    assert App.args is None
    with pytest.raises(SystemExit):
        App()
    assert isinstance(App.args, argparse.Namespace)


def test_CommandLineApp_attribute_defaults():
    App = csboilerplate.CommandLineApp(noop)
    assert App.name == sys.argv[0]
    assert App.exit is sys.exit


def test_CommandLineApp_name():
    App = csboilerplate.CommandLineApp(noop, name='test_name')
    assert App.name == 'test_name'


def test_CommandLineApp_exit_handler():
    exit = Mock()
    App = csboilerplate.CommandLineApp(noop, exit_handler=exit)
    assert App.exit is exit
    App()
    exit.assert_called_once()


def test_CommandLineApp_interrupt():
    interrupted = Mock(side_effect=KeyboardInterrupt)
    exit = Mock(side_effect=SystemExit)
    App = csboilerplate.CommandLineApp(interrupted, exit_handler=exit)
    with pytest.raises(SystemExit):
        App()
    exit.assert_called_once_with('KeyboardInterrupt')


def test_CommandLineApp_sigterm_handler():
    csboilerplate.CommandLineApp(noop, sigterm_handler=False)
    assert signal.getsignal(signal.SIGTERM) == signal.SIG_DFL
    csboilerplate.CommandLineApp(noop)
    assert callable(signal.getsignal(signal.SIGTERM))
    with pytest.raises(SystemExit):
        signal.getsignal(signal.SIGTERM)('signal', 'frame')
    csboilerplate.CommandLineApp(noop, sigterm_handler=noop)
    assert signal.getsignal(signal.SIGTERM) == noop


@patch('csboilerplate.logger.exception')
def test_CommandLineApp_uncaught_exception(logger_exception):
    broken = Mock(side_effect=ValueError)
    exit = Mock(side_effect=SystemExit)
    App = csboilerplate.CommandLineApp(broken, exit_handler=exit)
    with pytest.raises(SystemExit):
        App()
    exit.assert_called_once_with('uncaught exception')
    logger_exception.assert_called_once()
    assert isinstance(logger_exception.call_args[0][0], ValueError)


@patch('csboilerplate.logging.basicConfig')
def test_CommandLineApp_logging_config(basicConfig):
    App = csboilerplate.CommandLineApp(noop)
    App.logging_config(log_level=0)
    assert basicConfig.call_args[1]['level'] == logging.WARNING
    App.logging_config(log_level=1)
    assert basicConfig.call_args[1]['level'] == logging.INFO
    App.logging_config(log_level=2)
    assert basicConfig.call_args[1]['level'] == logging.DEBUG
    with pytest.raises(IndexError):
        App.logging_config(log_level=3)
    App.logging_config(handlers=[42])
    assert basicConfig.call_args[1]['handlers'] == [42]
    App.logging_config(log_level=3, log_levels=[0, 1, 2, 3])
    assert basicConfig.call_args[1]['level'] == 3
