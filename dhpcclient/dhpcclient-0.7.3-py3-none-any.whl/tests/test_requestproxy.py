
import pytest
from .context import requestproxy, taskhandler, hpcclient, task, tasklogger
from .create_test_data import task_outputs, tasks, clients
import requests
import json

url = 'http://localhost:8080/api'

@pytest.fixture
def request_proxy(mocker):
    auth_mock = mocker.patch('requests.post').return_value
    auth_mock.json.return_value = { 'id_token': 'TOKEN'}
    return requestproxy.RequestProxy(url)

def test_get(mocker, request_proxy):
    mock_rq = mocker.patch('requests.get')
    request_proxy.get(url+'/test')

    assert mock_rq.call_count == 1

def test_post(mocker, request_proxy):
    mock_rq = mocker.patch('requests.post')
    request_proxy.post(url + '/test', payload={'test': 'test'})

    assert mock_rq.call_count == 1

def test_put(mocker, request_proxy):
    mock_rq = mocker.patch('requests.put')
    request_proxy.put(url + '/test', payload={'test': 'test'})

    assert mock_rq.call_count == 1

def test_patch(mocker, request_proxy):
    mock_rq = mocker.patch('requests.patch')
    request_proxy.patch(url + '/test', payload={'test': 'test'})

    assert mock_rq.call_count == 1

def test_delete(mocker, request_proxy):
    mock_rq = mocker.patch('requests.delete')
    request_proxy.delete(url + '/test')

    assert mock_rq.call_count == 1

def test_getTasks(mocker, request_proxy):
    mocker.patch('requests.get')
    request_proxy.getTasks()
    requests.get.assert_called_once_with(url+'/tasks'+'',
                                         headers=request_proxy._headers, params=None)

def test_putTask(mocker, request_proxy):
    mocker.patch('requests.put')
    client = hpcclient.HPCClient(False)
    _task = task.Task(client, tasks)
    request_proxy.putTask(_task)
    requests.put.assert_called_once_with(url + '/tasks' + '', data=json.dumps(_task.json_repr()),
                                         headers=request_proxy._headers)

def test_getTask(mocker, request_proxy):
    mocker.patch('requests.get')
    request_proxy.getTask(1)
    requests.get.assert_called_once_with(url + '/tasks/1', headers=request_proxy._headers, params=None)

def test_postTaskOutput(mocker, request_proxy):
    client = hpcclient.HPCClient(False)
    _task = task.Task(client, tasks)
    _task.id = 1
    to = tasklogger.TaskLogger(_task)
    text = bytearray('test'.encode('utf-8'))
    to.write(text)
    mocker.patch('requests.post')
    request_proxy.postTaskOutput(to)
    requests.post.assert_called_once_with(url+'/tasks/1/task-outputs', data=json.dumps(to.json_repr()),
                                          headers=request_proxy._headers)

def test_putTaskOutput(mocker, request_proxy):
    client = hpcclient.HPCClient(False)
    _task = task.Task(client, tasks)
    _task.id = 1
    to = tasklogger.TaskLogger(_task)
    text = bytearray('test'.encode('utf-8'))
    to.write(text)
    mocker.patch('requests.put')
    request_proxy.putTaskOutput(to)
    requests.put.assert_called_once_with(url + '/tasks/1/task-outputs', data=json.dumps(to.json_repr()),
                                          headers=request_proxy._headers)

def test_patchTaskOutput(mocker, request_proxy):
    client = hpcclient.HPCClient(False)
    _task = task.Task(client, tasks)
    _task.id = 1
    to = tasklogger.TaskLogger(_task)
    to.id = 2
    text = bytearray('test'.encode('utf-8'))
    to.write(text)
    mocker.patch('requests.patch')
    request_proxy.patchTaskOutput(to)
    requests.patch.assert_called_once_with(url + '/tasks/1/task-outputs/2', data=json.dumps({'id': 2,
                                           'content': 'test', 'task': _task.json_repr()}),
                                            headers=request_proxy._headers)

def test_postClient(mocker, request_proxy):
    client = hpcclient.HPCClient(False)
    mocker.patch('requests.post')
    request_proxy.postClient(client)
    requests.post.assert_called_once_with(url + '/clients', data=json.dumps(client.json_repr()),
                                          headers=request_proxy._headers)
