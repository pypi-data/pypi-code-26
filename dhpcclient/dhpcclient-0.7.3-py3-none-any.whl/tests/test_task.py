
import pytest
import pytest_mock
import mock
from pytest_mock import mocker
import docker
from .context import taskhandler, hpcclient, task, requestproxy, tasklogger

task_json = {
  "clientId": None,
  "dockerImageUrl": "string",
  "durationMinutes": 0,
  "externalPort": 0,
  "internalPort": 0,
  "id": 0,
  "ioMountPathDst": None,
  "ioMountPathSrc": None,
  "name": "string",
  "priority": 0,
  "progress": 0,
  "requiredCPUs": 2,
  "requiredGBDiskSpace": 0,
  "requiredGBRAM": 0,
  "requiredGPUs": 0,
  "taskState": "CREATED",
  "taskZip": "string",
  "taskZipContentType": "string",
  "requiredOperatingSystem": "LINUX",
  "dockerImageType": 'WORKER'
}

@pytest.fixture
def get_task(mocker):
    mock_client = mocker.patch('hpcclient.hpcclient.HPCClient')
    mock_docker = mocker.patch('docker.from_env')
    mock_client.json_repr.return_value = { 'id': 1}

    tsk = task.Task(mock_client, task_json)

    assert mock_docker.call_count == 1

    return tsk

def test_determine_runtime_1(mocker, get_task):
    mock_client = mocker.patch('hpcclient.hpcclient.HPCClient', accessibleGPUs={'nvidia' : ""})

    get_task._client = mock_client
    get_task.requiredGPUs = 1

    ret = get_task._determine_runtime(get_task.requiredGPUs)

    assert ret == 'nvidia'

def test_determine_runtime_2(mocker, get_task):
    mock_client = mocker.patch('hpcclient.hpcclient.HPCClient', accessibleGPUs={'opencl' : ""})

    get_task._client = mock_client
    get_task.requiredGPUs = 1

    ret = get_task._determine_runtime(get_task.requiredGPUs)

    assert ret == 'oci'

def test_determine_runtime_3(mocker, get_task):
    mock_client = mocker.patch('hpcclient.hpcclient.HPCClient', accessibleGPUs={'opencl' : ""})

    get_task._client = mock_client
    get_task.requiredGPUs = 0

    ret = get_task._determine_runtime(get_task.requiredGPUs)

    assert ret == 'oci'

def test_pull_and_run_image(mocker, get_task):
    mock_client = mocker.patch('hpcclient.hpcclient.HPCClient', availableCPUs=4.)

    mock_docker = mocker.patch.object(get_task._docker.containers, 'run')
    get_task._client = mock_client
    get_task.pull_and_run_image()

    mock_docker.assert_called_once_with(get_task.dockerImageUrl, detach=True, mem_limit=str(get_task.requiredGBRAM)+'g',
                                                          cpu_quota=int(round(100000 * 0.5)), cpu_period=100000,
                                                          ports={ '0/tcp': 0 }, name='dhpc_task_0')

def test_extract_port(mocker, get_task):
    get_task.externalPort = '3333'
    get_task.internalPort = '2222'

    required_ports = { '2222/tcp': 3333 }
    ports = get_task._extract_port()

    assert len(ports.keys()) == 1
    assert required_ports.keys() == ports.keys()
    assert required_ports['2222/tcp'] == ports['2222/tcp']

def test_extract_port_typeError(mocker, get_task):
    get_task.externalPort = None

    with(pytest.raises(TypeError)):
        ports = get_task._extract_port()

def test_extract_port_typeError2(mocker, get_task):
    get_task.externalPort = None
    get_task.internalPort = 8080

    with(pytest.raises(TypeError)):
        ports = get_task._extract_port()

def test_extract_port_typeError3(mocker, get_task):
    get_task.externalPort = '70a'
    get_task.internalPort = 8080

    with(pytest.raises(ValueError)):
        ports = get_task._extract_port()

def test_create_path(mocker, get_task):
    get_task.ioMountPathDst = 'asdf'
    get_task.ioMountPathSrc = 'test'

    testval = get_task._create_path()

    assert len(testval.keys()) == 1
    assert list(testval.keys())[0] == 'test'
    assert testval['test']['bind'] == 'asdf'
    assert testval['test']['mode'] == 'rw'

def test_create_path2(mocker, get_task):
    get_task.ioMountPathDst = None
    get_task.ioMountPathSrc = 'test'

    with(pytest.raises(ValueError)):
        testval = get_task._create_path()