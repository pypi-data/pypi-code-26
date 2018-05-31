
import pytest
import pytest_mock
import mock
from pytest_mock import mocker
from .context import taskhandler, hpcclient, task, requestproxy, tasklogger


@pytest.fixture
def task_handler(mocker):
    client = mocker.patch('hpcclient.HPCClient')
    client.json_repr.return_value = { 'id': 1}

    proxy = mocker.patch.object(requestproxy.RequestProxy, 'getTask')
    proxy.return_value={'id': 2, 'imageURL': 'test'}

    _task = mocker.patch('task.Task')
    _task_i = _task.return_value
    _task_i.json_repr.return_value = { 'id': 1}
    _task_i.stop_container.return_value = True
    _task_i.container_running.return_value = False
    _task_i.remove_container.return_value = True
    _task_i.durationMinutes = 300

    return taskhandler.TaskHandler(client, proxy, _task_i)


def test_handle_task(mocker, task_handler):
    mocker.patch.object(tasklogger.TaskLogger, 'empty')

    task_handler.handle_task()

    assert task_handler._task.pull_and_run_image.call_count == 1
    assert task_handler._task.container_running.call_count == 1
    assert task_handler._task.remove_container.call_count == 1

@pytest.mark.skip
def test_handle_task_typeerror(mocker, task_handler):
    mocker.patch.object(tasklogger.TaskLogger, 'empty')
    mock_ts = mocker.patch.object(task_handler)
    mock_ts._taskconfig = {'id': 1, 'externalPort': None, 'dockerImageType': 'WORKER' }
    #task_handler._taskconfig.return_value =
    #print(str(task_handler._taskconfig))
    task_handler.handle_task()

    assert task_handler._task.taskState == 'FAILED'

def test_stop_task(mocker, task_handler):
    task_handler.handle_task()
    mock_ts = mocker.patch.object(task_handler._task, 'pause_container')
    task_handler.stop_task()
    assert mock_ts.call_count == 1

def test_restart_task(mocker, task_handler):
    task_handler.handle_task()
    mock_ts = mocker.patch.object(task_handler._task, 'unpause_container')
    task_handler.restart_task()
    assert mock_ts.call_count == 1