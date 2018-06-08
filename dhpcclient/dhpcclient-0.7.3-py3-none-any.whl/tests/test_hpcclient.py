
import pytest
#from pytest_mock import mocker
import configparser
from .context import hpcclient, requestproxy


@pytest.fixture
def hpc_client(mocker):
    mocker.patch('requests.post')
    auth_mock = mocker.patch('requests.post').return_value
    auth_mock.json.return_value = {'id_token': 'TOKEN'}
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


def test_init_conn_settings(mocker, hpc_client):
    mock_rqp = mocker.patch('requestproxy.RequestProxy')
    cfg = hpc_client._load_config()
    hpc_client._init_conn_settings(cfg)
    assert mock_rqp.call_count == 1

def test_increment_resources(mocker, hpc_client):
    mock_task = mocker.patch('hpcclient.task.Task')
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
    mock_task = mocker.patch('hpcclient.task.Task')
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
    mock_task = mocker.patch('hpcclient.task.Task')
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
    mock_task = mocker.patch('hpcclient.task.Task')
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
    mock_task = mocker.patch('hpcclient.task.Task')
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
    mock_task = mocker.patch('hpcclient.task.Task')
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
