import pcc
import os
from unittest.mock import patch, call
from contextlib import contextmanager


@contextmanager
def temp_file(file_path, file_text):
    with open(file_path, 'w') as f:
        f.write(file_text)
    yield f
    os.remove(file_path)


def test_load_scripts_returns_none_if_no_pcc_or_package():
    assert pcc.load_scripts() is None


def test_load_scripts_returns_data_from_pcc_json():
    write_scripts = """{"demo": "pytest"}"""
    with temp_file('pcc.json', write_scripts):
        scripts = pcc.load_scripts()
    assert scripts['demo'] == 'pytest'


def test_load_scripts_returns_data_from_package_json():
    write_scripts = """{"scripts": {"demo": "pytest"}}"""
    with temp_file('package.json', write_scripts):
        scripts = pcc.load_scripts()
    assert scripts['demo'] == 'pytest'


@patch('sys.argv', ['', 'custom command=python fuzzies.py'])
def test_parse_extra_commands():
    arg_data = pcc.parse_args()
    assert len(arg_data['extra']) == 1
    assert 'custom command' in arg_data['extra']
    assert arg_data['extra']['custom command'] == 'python fuzzies.py'


@patch('sys.argv', ['', 'command with equal=do something && x=y'])
def test_parse_arg_with_equal():
    arg_data = pcc.parse_args()
    assert arg_data['extra']['command with equal'] == 'do something && x=y'


@patch('sys.argv', ['', '--col=6'])
def test_parse_columns():
    arg_data = pcc.parse_args()
    assert arg_data['col'] == '6'


@patch('pcc.print')
def test_print_header_contains_lines(mock_print):
    pcc.print_header('a simple line')
    calls = [
        call('╔═══════════════╗'),
        call('║ a simple line ║'),
        call('╚═══════════════╝'),
    ]
    assert mock_print.call_args_list == calls


@patch('pcc.Popen')
def test_script_wrapper_would_start_process_with_a_list(mock_popen):
    wrapper = pcc.script_wrapper('command list')
    wrapper()
    mock_popen.called_with_args(['command', 'list'])
