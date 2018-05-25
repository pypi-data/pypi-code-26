import pytest
import mock
import re
from emlid.ardupilot.ardupilot import ArdupilotConfigurator, ArdupilotConfiguration, CannotConfigureException
from emlid.util.util import NotRootException


output_rover = "ardurover - auto mode\
                link currently points to /opt/ardupilot/navio/ardurover-3.1/bin/ardurover\n\
/opt/ardupilot/navio/ardurover-3.1/bin/ardurover - priority 50\n\
/opt/ardupilot/navio2/ardurover-3.1/bin/ardurover - priority 50\n\
Current 'best' version is '/opt/ardupilot/navio/ardurover-3.1/bin/ardurover'."

output_plane = "arduplane - auto mode\
  link currently points to /opt/ardupilot/navio/arduplane-3.7/bin/arduplane\n\
/opt/ardupilot/navio/arduplane-3.7/bin/arduplane - priority 50\n\
/opt/ardupilot/navio/arduplane-3.7/bin/arduplane-tri - priority 50\n\
/opt/ardupilot/navio2/arduplane-3.7/bin/arduplane - priority 50\n\
/opt/ardupilot/navio2/arduplane-3.7/bin/arduplane-tri - priority 50\n\
Current 'best' version is '/opt/ardupilot/navio/arduplane-3.7/bin/arduplane'."

output_copter = "arducopter - manual mode\
  link currently points to /opt/ardupilot/navio2/arducopter-3.5/bin/arducopter-heli\n\
/opt/ardupilot/navio/arducopter-3.4/bin/arducopter-coax - priority 50\n\
/opt/ardupilot/navio/arducopter-3.4/bin/arducopter-heli - priority 50\n\
/opt/ardupilot/navio/arducopter-3.4/bin/arducopter-hexa - priority 50\n\
/opt/ardupilot/navio/arducopter-3.4/bin/arducopter-octa - priority 50\n\
/opt/ardupilot/navio/arducopter-3.4/bin/arducopter-octa-quad - priority 50\n\
/opt/ardupilot/navio/arducopter-3.4/bin/arducopter-quad - priority 50\n\
/opt/ardupilot/navio/arducopter-3.4/bin/arducopter-single - priority 50\n\
/opt/ardupilot/navio/arducopter-3.4/bin/arducopter-tri - priority 50\n\
/opt/ardupilot/navio/arducopter-3.4/bin/arducopter-y6 - priority 50\n\
/opt/ardupilot/navio2/arducopter-3.4/bin/arducopter-coax - priority 50\n\
/opt/ardupilot/navio2/arducopter-3.4/bin/arducopter-heli - priority 50\n\
/opt/ardupilot/navio2/arducopter-3.4/bin/arducopter-hexa - priority 50\n\
/opt/ardupilot/navio2/arducopter-3.4/bin/arducopter-octa - priority 50\n\
/opt/ardupilot/navio2/arducopter-3.4/bin/arducopter-octa-quad - priority 50\n\
/opt/ardupilot/navio2/arducopter-3.4/bin/arducopter-quad - priority 50\n\
/opt/ardupilot/navio2/arducopter-3.4/bin/arducopter-single - priority 50\n\
/opt/ardupilot/navio2/arducopter-3.4/bin/arducopter-tri - priority 50\n\
/opt/ardupilot/navio2/arducopter-3.4/bin/arducopter-y6 - priority 50\n\
/opt/ardupilot/navio2/arducopter-3.5/bin/arducopter - priority 50\n\
/opt/ardupilot/navio2/arducopter-3.5/bin/arducopter-heli - priority 50\n\
Current 'best' version is '/opt/ardupilot/navio2/arducopter-3.5/bin/arducopter-heli'."

def return_fake_version(vehicle, product):
    if vehicle is 'copter':
        return 'somepath3.4othertext\nsomepath3.5othertext'
    elif vehicle is 'plane':
        return '3.7'
    else:
        return '3.1'


def get_fake_frames(self, vehicle, product, version):
    if vehicle is 'copter':
        output = output_copter
    elif vehicle is 'plane':
        output = output_plane
    else:
        output = output_rover
    available_frames = ''
    for alternative in output.splitlines():
        if '/' + product + '/' in alternative:
            if '/ardu' + vehicle + '-' + version + '/' in alternative:
                available_frames += alternative + '\n'
    frames = list(map(lambda s: s[:-2], re.findall(r'ardu' + vehicle + '-?[a-z-0-9]* -', available_frames)))
    return frames


@pytest.fixture
def stub_tester():
    configurator = ArdupilotConfigurator("Navio+")
    configurator.board.get_all_versions = return_fake_version
    configurator.board.get_frames = get_fake_frames
    return configurator


@pytest.fixture
def stub_tester_navio2():
    configurator = ArdupilotConfigurator("Navio2")
    return configurator


def test_get_product_navio(stub_tester):
    assert stub_tester.board.get_product() == 'navio'


def test_get_product_navio2(stub_tester_navio2):
    assert stub_tester_navio2.board.get_product() == 'navio2'


def test_ask_for_choice(stub_tester):
    with mock.patch('builtins.input', return_value='1'):
                assert stub_tester.ask_for_choice(stub_tester.vehicles, 'vehicle') == '1'
    with mock.patch('builtins.input', return_value='2'):
                assert stub_tester.ask_for_choice(stub_tester.vehicles, 'vehicle') == '2'
    with mock.patch('builtins.input', return_value='3'):
                assert stub_tester.ask_for_choice(stub_tester.vehicles, 'vehicle') == '3'


def test_get_choice_vehicle(stub_tester):
    with mock.patch('builtins.input', return_value='1'):
                assert stub_tester.get_choice(stub_tester.vehicles, 'vehicle') == 'copter'
    with mock.patch('builtins.input', return_value='2'):
                assert stub_tester.get_choice(stub_tester.vehicles, 'vehicle') == 'plane'
    with mock.patch('builtins.input', return_value='3'):
                assert stub_tester.get_choice(stub_tester.vehicles, 'vehicle') == 'rover'
    with mock.patch('builtins.input', return_value='0'):
        with pytest.raises(IndexError):
            stub_tester.get_choice(stub_tester.vehicles, 'vehicle')
    with mock.patch('builtins.input', return_value='random text'):
        with pytest.raises(ValueError):
            stub_tester.get_choice(stub_tester.vehicles, 'vehicle')


def test_get_choice_frame_for_copter(stub_tester):
    frames = stub_tester.board.get_frames(stub_tester, 'copter', 'navio2', '3.4')
    with mock.patch('builtins.input', return_value='1'):
                assert stub_tester.get_choice(frames, 'frame') == 'arducopter-coax'
    with mock.patch('builtins.input', return_value='2'):
                assert stub_tester.get_choice(frames, 'frame') == 'arducopter-heli'
    with mock.patch('builtins.input', return_value='3'):
                assert stub_tester.get_choice(frames, 'frame') == 'arducopter-hexa'
    with mock.patch('builtins.input', return_value='4'):
                assert stub_tester.get_choice(frames, 'frame') == 'arducopter-octa'
    with mock.patch('builtins.input', return_value='5'):
                assert stub_tester.get_choice(frames, 'frame') == 'arducopter-octa-quad'
    with mock.patch('builtins.input', return_value='6'):
                assert stub_tester.get_choice(frames, 'frame') == 'arducopter-quad'
    with mock.patch('builtins.input', return_value='7'):
                assert stub_tester.get_choice(frames, 'frame') == 'arducopter-single'
    with mock.patch('builtins.input', return_value='8'):
                assert stub_tester.get_choice(frames, 'frame') == 'arducopter-tri'
    with mock.patch('builtins.input', return_value='9'):
                assert stub_tester.get_choice(frames, 'frame') == 'arducopter-y6'
    with mock.patch('builtins.input', return_value='0'):
        with pytest.raises(IndexError):
            stub_tester.get_choice(frames, 'vehicle')
    with mock.patch('builtins.input', return_value='random text'):
        with pytest.raises(ValueError):
            stub_tester.get_choice(frames, 'vehicle')


def test_get_choice_frame_for_plane(stub_tester):
    frames = stub_tester.board.get_frames(stub_tester, 'plane', 'navio2', '3.7')
    with mock.patch('builtins.input', return_value='1'):
                assert stub_tester.get_choice(frames, 'frame') == 'arduplane'
    with mock.patch('builtins.input', return_value='2'):
                assert stub_tester.get_choice(frames, 'frame') == 'arduplane-tri'
    with mock.patch('builtins.input', return_value='0'):
        with pytest.raises(IndexError):
            stub_tester.get_choice(frames, 'vehicle')
    with mock.patch('builtins.input', return_value='random text'):
        with pytest.raises(ValueError):
            stub_tester.get_choice(frames, 'vehicle')


def test_get_configuration_not_root(stub_tester, capsys):
    with pytest.raises(NotRootException):
        stub_tester.get_configuration()


def test_configure(stub_tester):
    configuration = ArdupilotConfiguration('navio', 'copter', 'arducopter-coax', '3.4')
    with pytest.raises(CannotConfigureException) as e:
        stub_tester.configure(configuration)


def test_get_choice_frame_for_rover(stub_tester):
    frames = stub_tester.board.get_frames(stub_tester, 'rover', 'navio2', '3.1')
    assert stub_tester.get_choice(frames, 'frame') == 'ardurover'


def test_get_version_for_copter(stub_tester):
    with mock.patch('builtins.input', return_value='1'):
        assert stub_tester.board.get_versions('copter', 'navio2') == ['3.4', '3.5']


def test_get_version_for_plane(stub_tester):
    assert stub_tester.board.get_versions('plane', 'navio2') == ['3.7']


def test_get_version_for_rover(stub_tester):
    assert stub_tester.board.get_versions('rover', 'navio2') == ['3.1']
