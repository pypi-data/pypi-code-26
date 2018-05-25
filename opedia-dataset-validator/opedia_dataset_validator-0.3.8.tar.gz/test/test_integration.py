import opedia_dataset_validator as odv
import os
import pytest

@pytest.fixture
def runner():
    from click.testing import CliRunner
    return CliRunner()


@pytest.fixture
def excel_file1():
    return os.path.join('test', 'data', 'AllErrors_2018-05-19_v1.0.xlsx')


@pytest.fixture
def excel_file2():
    return os.path.join('test', 'data', 'CustomDataErrors_2018-05-19_v1.0.xlsx')


def test_excel_file_integration(runner, excel_file1):
    result = runner.invoke(odv.cli.main, [excel_file1, '-'])
    lines = result.output.rstrip().split(os.linesep)
    assert result.exit_code == 0
    assert len(lines) == 14
    assert lines[0].split('\t') == ['#sheet', 'column', 'row', 'message']
    for line in lines:
        assert len(line.split('\t')) == 4


def test_excel_file_integration_all(runner, excel_file1):
    result = runner.invoke(odv.cli.main, ['-a', excel_file1, '-'])
    lines = result.output.rstrip().split(os.linesep)
    assert result.exit_code == 0
    assert len(lines) == 20
    assert lines[0].split('\t') == ['#sheet', 'column', 'row', 'message']
    for line in lines:
        assert len(line.split('\t')) == 4


def test_excel_file_integration_values(runner, excel_file1):
    result = runner.invoke(odv.cli.main, ['-v', excel_file1, '-'])
    lines = result.output.rstrip().split(os.linesep)
    assert result.exit_code == 0
    assert len(lines) == 14
    assert lines[0].split('\t') == ['#sheet', 'column', 'row', 'value', 'message']
    for line in lines:
        assert len(line.split('\t')) == 5


def test_excel_file_integration_custom_data(runner, excel_file2):
    result = runner.invoke(odv.cli.main, [excel_file2, '-'])
    lines = result.output.rstrip().split(os.linesep)
    assert result.exit_code == 0
    assert len(lines) == 2
    assert lines[0].split('\t') == ['#sheet', 'column', 'row', 'message']
    for line in lines:
        assert len(line.split('\t')) == 4
