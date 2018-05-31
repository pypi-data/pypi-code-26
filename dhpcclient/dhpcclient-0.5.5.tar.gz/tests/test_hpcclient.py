
import pytest
import configparser
from .context import hpcclient, requestproxy, task
import logging


@pytest.fixture
def hpc_client(mocker):
    mocker.patch('requests.post')
    auth_mock = mocker.patch('requests.post').return_value
    auth_mock.json.return_value = {'id_token': 'TOKEN'}
    clnt_req_mock = mocker.patch('requestproxy.RequestProxy.postClient')
    clnt_req_get_mock = mocker.patch('requestproxy.RequestProxy.getClient')
    clnt_req_mock.return_value = {'id': 0}
    clnt_req_get_mock.return_value = {'version': 1}
    dns_res_mock = mocker.MagicMock(address='127.0.0.1')
    dckr_client_mock=mocker.patch('docker.DockerClient')
    dckr_client_mock.version.return_value={'Os': 'linux'}
    clnt_docker_mock = mocker.patch('docker.from_env')
    clnt_docker_mock.return_value = dckr_client_mock

    dns_mock = mocker.patch('dns.resolver.query')
    dns_mock.return_value = [dns_res_mock]

    return hpcclient.HPCClient(False)

def test_load_config(mocker, hpc_client):
    mock_cp = mocker.patch('configparser.ConfigParser.read')
    #mock_cp.read.return_value = 'read'
    hpc_client._load_config()
    assert mock_cp.call_count == 1


@pytest.mark.skip
def test_save_config(mocker, hpc_client):
    mock_cp = mocker.patch('configparser.ConfigParser.write')
    #
    cfg = hpc_client._load_config()
    # Deletes config contents - dunno why
    hpc_client._save_config(cfg)
    assert mock_cp.call_count == 1

def test_increment_resources(mocker, hpc_client):
    mock_task = mocker.patch('task.Task')
    mock_task = mock_task.return_value

    mock_task.requiredGPUs.return_value = 1
    mock_task.requiredGBRAM.return_value = 2
    mock_task.requiredGBDiskSpace.return_value = 4
    mock_task.requiredCPUs.return_value = 2

    gpus = hpc_client.availableGPUs
    gbram = hpc_client.availableGBRAM
    gbdiskspace = hpc_client.availableGBDiskSpace
    cpus = hpc_client.availableCPUs

    hpc_client.increment_resources(mock_task)

    assert gpus + mock_task.requiredGPUs == hpc_client.availableGPUs
    assert gbram + mock_task.requiredGBRAM == hpc_client.availableGBRAM
    assert gbdiskspace + mock_task.requiredGBDiskSpace == hpc_client.availableGBDiskSpace
    assert cpus + mock_task.requiredCPUs == hpc_client.availableCPUs

def test_decrement_resources(mocker, hpc_client):
    mock_task = mocker.patch('task.Task')
    mock_task = mock_task.return_value

    hpc_client.availableCPUs = 5
    hpc_client.availableGBDiskSpace = 5
    hpc_client.availableGBRAM = 5
    hpc_client.availableGPUs = 5

    mock_task.requiredGPUs = 1
    mock_task.requiredGBRAM = 2
    mock_task.requiredGBDiskSpace = 4
    mock_task.requiredCPUs = 2

    gpus = hpc_client.availableGPUs
    gbram = hpc_client.availableGBRAM
    gbdiskspace = hpc_client.availableGBDiskSpace
    cpus = hpc_client.availableCPUs

    hpc_client.decrement_resources(mock_task)

    assert gpus - mock_task.requiredGPUs == hpc_client.availableGPUs
    assert gbram - mock_task.requiredGBRAM == hpc_client.availableGBRAM
    assert gbdiskspace - mock_task.requiredGBDiskSpace == hpc_client.availableGBDiskSpace
    assert cpus - mock_task.requiredCPUs == hpc_client.availableCPUs


def test_decrement_resources_error1(mocker, hpc_client):
    mock_task = mocker.patch('task.Task')
    mock_task = mock_task.return_value

    mock_task.requiredGPUs = 100
    mock_task.requiredGBRAM = 2
    mock_task.requiredGBDiskSpace = 4
    mock_task.requiredCPUs = 2

    gpus = hpc_client.availableGPUs
    gbram = hpc_client.availableGBRAM
    gbdiskspace = hpc_client.availableGBDiskSpace
    cpus = hpc_client.availableCPUs

    with(pytest.raises(ValueError)):
        hpc_client.decrement_resources(mock_task)

def test_decrement_resources_error2(mocker, hpc_client):
    mock_task = mocker.patch('task.Task')
    mock_task = mock_task.return_value

    mock_task.requiredGPUs = 1
    mock_task.requiredGBRAM = 200
    mock_task.requiredGBDiskSpace = 4
    mock_task.requiredCPUs = 2

    gpus = hpc_client.availableGPUs
    gbram = hpc_client.availableGBRAM
    gbdiskspace = hpc_client.availableGBDiskSpace
    cpus = hpc_client.availableCPUs

    with(pytest.raises(ValueError)):
        hpc_client.decrement_resources(mock_task)

def test_decrement_resources_error3(mocker, hpc_client):
    mock_task = mocker.patch('task.Task')
    mock_task = mock_task.return_value

    mock_task.requiredGPUs = 1
    mock_task.requiredGBRAM = 2
    mock_task.requiredGBDiskSpace = 400
    mock_task.requiredCPUs = 2

    gpus = hpc_client.availableGPUs
    gbram = hpc_client.availableGBRAM
    gbdiskspace = hpc_client.availableGBDiskSpace
    cpus = hpc_client.availableCPUs

    with(pytest.raises(ValueError)):
        hpc_client.decrement_resources(mock_task)

def test_decrement_resources_error4(mocker, hpc_client):
    mock_task = mocker.patch('task.Task')
    mock_task = mock_task.return_value

    mock_task.requiredGPUs = 1
    mock_task.requiredGBRAM = 2
    mock_task.requiredGBDiskSpace = 4
    mock_task.requiredCPUs = 200

    gpus = hpc_client.availableGPUs
    gbram = hpc_client.availableGBRAM
    gbdiskspace = hpc_client.availableGBDiskSpace
    cpus = hpc_client.availableCPUs

    with(pytest.raises(ValueError)):
        hpc_client.decrement_resources(mock_task)

def test_get_nvgpus(mocker, hpc_client):
    mock_q_smvi = mocker.patch('nvidia.query_nvsmi')
    hpc_client._get_nvgpus()
    assert mock_q_smvi.call_count == 1

def test_get_nvgpus(mocker, hpc_client):
    mock_q_clinfo = mocker.patch('amd.query_clinfo')
    hpc_client._get_clgpus()
    assert mock_q_clinfo.call_count == 1
