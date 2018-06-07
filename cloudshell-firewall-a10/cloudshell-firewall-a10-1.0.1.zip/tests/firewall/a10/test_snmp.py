from mock import patch, MagicMock

from cloudshell.firewall.a10.helpers.exceptions import A10Exception
from cloudshell.firewall.a10.runners.a10_autoload_runner import A10AutoloadRunner
from cloudshell.firewall.a10.snmp.a10_snmp_handler import A10SnmpHandler
from tests.firewall.a10.base_test import BaseA10TestCase, CliEmulator, Command, CONFIG_PROMPT


@patch('cloudshell.devices.snmp_handler.QualiSnmp', MagicMock())
@patch('cloudshell.firewall.a10.flows.a10_autoload_flow.A10SNMPAutoload', MagicMock())
@patch('cloudshell.cli.session.ssh_session.paramiko', MagicMock())
@patch('cloudshell.cli.session.ssh_session.SSHSession._clear_buffer', MagicMock(return_value=''))
@patch('time.sleep', MagicMock())
class TestEnableDisableSnmp(BaseA10TestCase):

    def _setUp(self, attrs=None):
        attrs = attrs or {}
        snmp_attrs = {
            'SNMP Version': 'v2c',
            'SNMP Read Community': 'public',
            'SNMP V3 User': 'quali_user',
            'SNMP V3 Password': 'password',
            'SNMP V3 Private Key': 'private_key',
            'SNMP V3 Authentication Protocol': 'No Authentication Protocol',
            'SNMP V3 Privacy Protocol': 'No Privacy Protocol',
            'Enable SNMP': 'True',
            'Disable SNMP': 'False',
        }
        snmp_attrs.update(attrs)
        super(TestEnableDisableSnmp, self)._setUp(snmp_attrs)
        self.snmp_handler = A10SnmpHandler(
            self.resource_config, self.logger, self.api, self.cli_handler)
        self.runner = A10AutoloadRunner(self.resource_config, self.logger, self.snmp_handler)

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_enable_snmp_v2(self, send_mock, recv_mock):
        self._setUp()

        emu = CliEmulator([
            Command('configure', CONFIG_PROMPT),
            Command('snmp-server enable service', CONFIG_PROMPT),
            Command(
                'snmp-server SNMPv1-v2c user quali_user',
                'vThunder(config-user:quali)(NOLICENSE)#'),
            Command('community read public', 'vThunder(config-user:quali)(NOLICENSE)#'),
            Command('exit', CONFIG_PROMPT),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    def test_enable_snmp_v2_write_community(self):
        self._setUp({'SNMP Write Community': 'private'})

        self.assertRaisesRegexp(
            A10Exception,
            '^ACOS devices doesn\'t support write communities$',
            self.runner.discover,
        )

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_disable_snmp_v2(self, send_mock, recv_mock):
        self._setUp({
            'Enable SNMP': 'False',
            'Disable SNMP': 'True',
        })

        emu = CliEmulator([
            Command('configure', CONFIG_PROMPT),
            Command('no snmp-server SNMPv1-v2c user quali_user', CONFIG_PROMPT),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    def test_disable_snmp_v2_write_community(self):
        self._setUp({
            'Enable SNMP': 'False',
            'Disable SNMP': 'True',
            'SNMP Write Community': 'private',
        })

        self.assertRaisesRegexp(
            A10Exception,
            '^ACOS devices doesn\'t support write communities$',
            self.runner.discover,
        )

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_enable_snmp_v3(self, send_mock, recv_mock):
        self._setUp({'SNMP Version': 'v3'})

        emu = CliEmulator([
            Command('configure', CONFIG_PROMPT),
            Command('snmp-server enable service', CONFIG_PROMPT),
            Command(
                'show running-config snmp-server',
                '!Section configuration: 328 bytes\n'
                '!\n'
                'snmp-server enable service\n'
                '!\n'
                'snmp-server view quali_view 1 included\n'
                '!\n'
                'snmp-server group quali_group v3 noauth read quali_view\n'
                '!\n'
                'snmp-server SNMPv3 user other_user group quali_group v3 noauth\n'
                '!\n'
                '{}'.format(CONFIG_PROMPT),
            ),
            Command('snmp-server view quali_view 1 included', CONFIG_PROMPT),
            Command('snmp-server group quali_group v3 noauth read quali_view', CONFIG_PROMPT),
            Command(
                'snmp-server SNMPv3 user quali_user group quali_group v3 noauth', CONFIG_PROMPT),
            Command(
                'show running-config snmp-server',
                '!Section configuration: 328 bytes\n'
                '!\n'
                'snmp-server enable service\n'
                '!\n'
                'snmp-server view quali_view 1 included\n'
                '!\n'
                'snmp-server group quali_group v3 noauth read quali_view\n'
                '!\n'
                'snmp-server SNMPv3 user quali_user group quali_group v3 noauth\n'
                '!\n'
                '{}'.format(CONFIG_PROMPT),
            ),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_snmp_v3_user_already_created(self, send_mock, recv_mock):
        self._setUp({'SNMP Version': 'v3'})

        emu = CliEmulator([
            Command('configure', CONFIG_PROMPT),
            Command('snmp-server enable service', CONFIG_PROMPT),
            Command(
                'show running-config snmp-server',
                '!Section configuration: 328 bytes\n'
                '!\n'
                'snmp-server enable service\n'
                '!\n'
                'snmp-server view quali_view 1 included\n'
                '!\n'
                'snmp-server group quali_group v3 noauth read quali_view\n'
                '!\n'
                'snmp-server SNMPv3 user quali_user group quali_group v3 noauth\n'
                '!\n'
                '{}'.format(CONFIG_PROMPT),
            ),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_snmp_v3_user_didnt_created(self, send_mock, recv_mock):
        self._setUp({'SNMP Version': 'v3'})

        emu = CliEmulator([
            Command('configure', CONFIG_PROMPT),
            Command('snmp-server enable service', CONFIG_PROMPT),
            Command('show running-config snmp-server', CONFIG_PROMPT),  # nothing is configured
            Command('snmp-server view quali_view 1 included', CONFIG_PROMPT),
            Command('snmp-server group quali_group v3 noauth read quali_view', CONFIG_PROMPT),
            Command(
                'snmp-server SNMPv3 user quali_user group quali_group v3 noauth', CONFIG_PROMPT),
            Command(
                'show running-config snmp-server',
                '!Section configuration: 328 bytes\n'
                '!\n'
                'snmp-server enable service\n'
                '!\n'
                'snmp-server view quali_view 1 included\n'
                '!\n'
                'snmp-server group quali_group v3 noauth read quali_view\n'
                '!\n'
                # didn't created user by some mistake
                # 'snmp-server SNMPv3 user quali_user group quali_group v3 noauth\n'
                # '!\n'
                '{}'.format(CONFIG_PROMPT),
            ),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.assertRaisesRegexp(
            A10Exception,
            r'^Failed to create SNMP User quali_user$',
            self.runner.discover,
        )

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_enable_snmp_v3_with_auth(self, send_mock, recv_mock):
        self._setUp({
            'SNMP Version': 'v3',
            'SNMP V3 Authentication Protocol': 'MD5',
        })

        emu = CliEmulator([
            Command('configure', CONFIG_PROMPT),
            Command('snmp-server enable service', CONFIG_PROMPT),
            Command('show running-config snmp-server', CONFIG_PROMPT),
            Command('snmp-server view quali_view 1 included', CONFIG_PROMPT),
            Command('snmp-server group quali_group v3 auth read quali_view', CONFIG_PROMPT),
            Command(
                'snmp-server SNMPv3 user quali_user group quali_group v3 auth md5 password',
                CONFIG_PROMPT,
            ),
            Command(
                'show running-config snmp-server',
                '!Section configuration: 328 bytes\n'
                '!\n'
                'snmp-server enable service\n'
                '!\n'
                'snmp-server view quali_view 1 included\n'
                '!\n'
                'snmp-server group quali_group v3 auth read quali_view\n'
                '!\n'
                'snmp-server SNMPv3 user quali_user group quali_group v3 auth md5 encrypted '
                '!encrypted password!\n'
                '!\n'
                '{}'.format(CONFIG_PROMPT),
            ),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_enable_snmp_v3_with_auth_and_priv(self, send_mock, recv_mock):
        self._setUp({
            'SNMP Version': 'v3',
            'SNMP V3 Authentication Protocol': 'SHA',
            'SNMP V3 Privacy Protocol': 'AES-128',
        })

        emu = CliEmulator([
            Command('configure', CONFIG_PROMPT),
            Command('snmp-server enable service', CONFIG_PROMPT),
            Command('show running-config snmp-server', CONFIG_PROMPT),
            Command('snmp-server view quali_view 1 included', CONFIG_PROMPT),
            Command('snmp-server group quali_group v3 priv read quali_view', CONFIG_PROMPT),
            Command(
                'snmp-server SNMPv3 user quali_user group quali_group v3 auth sha password '
                'priv aes private_key',
                CONFIG_PROMPT,
            ),
            Command(
                'show running-config snmp-server',
                '!Section configuration: 328 bytes\n'
                '!\n'
                'snmp-server enable service\n'
                '!\n'
                'snmp-server view quali_view 1 included\n'
                '!\n'
                'snmp-server group quali_group v3 priv read quali_view\n'
                '!\n'
                'snmp-server SNMPv3 user quali_user group quali_group v3 auth sha encrypted '
                '!encrypted password! priv aes encrypted !encrypted key!\n'
                '!\n'
                '{}'.format(CONFIG_PROMPT),
            ),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    def test_enable_snmp_v3_with_not_supported_priv_protocol(self):
        self._setUp({
            'SNMP Version': 'v3',
            'SNMP V3 Authentication Protocol': 'SHA',
            'SNMP V3 Privacy Protocol': 'AES-192',
        })

        self.assertRaisesRegexp(
            A10Exception,
            'Doen\'t supported private key protocol AES-192',
            self.runner.discover,
        )

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_disable_snmp_v3(self, send_mock, recv_mock):
        self._setUp({
            'SNMP Version': 'v3',
            'SNMP V3 Authentication Protocol': 'SHA',
            'SNMP V3 Privacy Protocol': 'AES-128',
            'Enable SNMP': 'False',
            'Disable SNMP': 'True',
        })

        emu = CliEmulator([
            Command('configure', CONFIG_PROMPT),
            Command('snmp-server enable service', CONFIG_PROMPT),
            Command(
                'show running-config snmp-server',
                '!Section configuration: 328 bytes\n'
                '!\n'
                'snmp-server enable service\n'
                '!\n'
                'snmp-server view quali_view 1 included\n'
                '!\n'
                'snmp-server group quali_group v3 priv read quali_view\n'
                '!\n'
                'snmp-server SNMPv3 user quali_user group quali_group v3 auth sha encrypted '
                '!encrypted password! priv aes encrypted !encrypted key!\n'
                '!\n'
                '{}'.format(CONFIG_PROMPT),
            ),
            Command(
                'no snmp-server SNMPv3 user quali_user group quali_group v3 auth sha password '
                'priv aes private_key',
                CONFIG_PROMPT,
            ),
            Command('no snmp-server group quali_group v3 priv read quali_view', CONFIG_PROMPT),
            Command('no snmp-server view quali_view 1 included', CONFIG_PROMPT),
            Command('show running-config snmp-server', CONFIG_PROMPT),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    def test_disable_snmp_v3_with_not_supported_priv_protocol(self):
        self._setUp({
            'SNMP Version': 'v3',
            'SNMP V3 Authentication Protocol': 'SHA',
            'SNMP V3 Privacy Protocol': 'AES-192',
            'Enable SNMP': 'False',
            'Disable SNMP': 'True',
        })

        self.assertRaisesRegexp(
            A10Exception,
            'Doen\'t supported private key protocol AES-192',
            self.runner.discover,
        )

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_remove_snmp_v3_user_already_deleted(self, send_mock, recv_mock):
        self._setUp({
            'SNMP Version': 'v3',
            'Enable SNMP': 'False',
            'Disable SNMP': 'True',
        })

        emu = CliEmulator([
            Command('configure', CONFIG_PROMPT),
            Command('snmp-server enable service', CONFIG_PROMPT),
            Command('show running-config snmp-server', CONFIG_PROMPT),  # snmp didn't enabled
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_snmp_v3_user_didnt_deleted(self, send_mock, recv_mock):
        self._setUp({
            'SNMP Version': 'v3',
            'Enable SNMP': 'False',
            'Disable SNMP': 'True',
        })

        emu = CliEmulator([
            Command('configure', CONFIG_PROMPT),
            Command('snmp-server enable service', CONFIG_PROMPT),
            Command(
                'show running-config snmp-server',
                '!Section configuration: 328 bytes\n'
                '!\n'
                'snmp-server enable service\n'
                '!\n'
                'snmp-server view quali_view 1 included\n'
                '!\n'
                'snmp-server group quali_group v3 noauth read quali_view\n'
                '!\n'
                'snmp-server SNMPv3 user quali_user group quali_group v3 noauth\n'
                '!\n'
                '{}'.format(CONFIG_PROMPT),
            ),
            Command(
                'no snmp-server SNMPv3 user quali_user group quali_group v3 noauth', CONFIG_PROMPT),
            Command('no snmp-server group quali_group v3 noauth read quali_view', CONFIG_PROMPT),
            Command('no snmp-server view quali_view 1 included', CONFIG_PROMPT),
            Command(
                'show running-config snmp-server',
                '!Section configuration: 328 bytes\n'
                '!\n'
                'snmp-server enable service\n'
                '!\n'
                'snmp-server view quali_view 1 included\n'
                '!\n'
                'snmp-server group quali_group v3 noauth read quali_view\n'
                '!\n'
                'snmp-server SNMPv3 user quali_user group quali_group v3 noauth\n'
                '!\n'
                '{}'.format(CONFIG_PROMPT),
            ),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.assertRaisesRegexp(
            A10Exception,
            r'^Failed to disable SNMP User quali_user$',
            self.runner.discover,
        )

        emu.check_calls()


class TestSnmpAutoload(BaseA10TestCase):
    def _setUp(self, attrs=None):
        attrs = attrs or {}
        snmp_attrs = {
            'SNMP Version': 'v2c',
            'SNMP Read Community': 'public',
            'Enable SNMP': 'False',
            'Disable SNMP': 'False',
        }
        snmp_attrs.update(attrs)
        super(TestSnmpAutoload, self)._setUp(snmp_attrs)
        self.snmp_handler = A10SnmpHandler(
            self.resource_config, self.logger, self.api, self.cli_handler)
        self.runner = A10AutoloadRunner(self.resource_config, self.logger, self.snmp_handler)

    def setUp(self):
        self._setUp()

    @patch('cloudshell.devices.snmp_handler.QualiSnmp')
    def test_autoload(self, snmp_mock):
        property_map = {
            ('SNMPv2-MIB', 'sysDescr', '0'):
                'Thunder Series Unified Application Service Gateway vThunder, ACOS 4.1.0-P10,',
            ('SNMPv2-MIB', 'sysContact', '0'): 'admin',
            ('SNMPv2-MIB', 'sysName', '0'): 'A10',
            ('SNMPv2-MIB', 'sysLocation', '0'): 'somewhere',
            ('SNMPv2-MIB', 'sysObjectID', '0'): 'A10-COMMON-MIB::a10AX.13',
            ('A10-AX-MIB', 'axSysSerialNumber', 0): '12345678',
            ('IF-MIB', 'ifType', 1): "'ethernetCsmacd'",
            ('IF-MIB', 'ifType', 2): "'ethernetCsmacd'",
            ('IF-MIB', 'ifType', 3): "'ethernetCsmacd'",
            ('IF-MIB', 'ifType', 4): "'ethernetCsmacd'",
        }
        table_map = {
            ('A10-AX-MIB', 'axInterfaceTable'): {
                1: {'axInterfaceMediaMaxSpeed': '10000', 'suffix': '1',
                    'axInterfaceAdminStatus': "'true'", 'axInterfaceIndex': '1',
                    'axInterfaceMediaMaxDuplex': "'auto'",
                    'axInterfaceFlowCtrlAdminStatus': "'disabled'", 'axInterfaceMtu': '1500',
                    'axInterfaceMediaActiveDuplex': "'full'", 'axInterfaceName': 'Ethernet 1',
                    'axInterfaceStatus': "'up'", 'axInterfaceMediaActiveSpeed': '10000',
                    'axInterfaceAlias': '', 'axInterfaceMacAddr': '52:54:00:97:83:4e',
                    'axInterfaceFlowCtrlOperStatus': "'false'"},
                2: {'axInterfaceMediaMaxSpeed': '0', 'suffix': '2',
                    'axInterfaceAdminStatus': "'false'", 'axInterfaceIndex': '2',
                    'axInterfaceMediaMaxDuplex': "'auto'",
                    'axInterfaceFlowCtrlAdminStatus': "'disabled'", 'axInterfaceMtu': '1500',
                    'axInterfaceMediaActiveDuplex': "'none'", 'axInterfaceName': 'Ethernet 2',
                    'axInterfaceStatus': "'disabled'", 'axInterfaceMediaActiveSpeed': '0',
                    'axInterfaceAlias': '', 'axInterfaceMacAddr': '52:54:00:04:68:a3',
                    'axInterfaceFlowCtrlOperStatus': "'false'"},
                3: {'axInterfaceMediaMaxSpeed': '10000', 'suffix': '3',
                    'axInterfaceAdminStatus': "'true'", 'axInterfaceIndex': '3',
                    'axInterfaceMediaMaxDuplex': "'auto'",
                    'axInterfaceFlowCtrlAdminStatus': "'disabled'", 'axInterfaceMtu': '1500',
                    'axInterfaceMediaActiveDuplex': "'full'", 'axInterfaceName': 'Ethernet 3',
                    'axInterfaceStatus': "'up'", 'axInterfaceMediaActiveSpeed': '10000',
                    'axInterfaceAlias': '', 'axInterfaceMacAddr': '52:54:00:e6:c5:63',
                    'axInterfaceFlowCtrlOperStatus': "'false'"},
                4: {'axInterfaceMediaMaxSpeed': '10000', 'suffix': '4',
                    'axInterfaceAdminStatus': "'true'", 'axInterfaceIndex': '4',
                    'axInterfaceMediaMaxDuplex': "'auto'",
                    'axInterfaceFlowCtrlAdminStatus': "'disabled'", 'axInterfaceMtu': '1500',
                    'axInterfaceMediaActiveDuplex': "'full'", 'axInterfaceName': 'Ethernet 4',
                    'axInterfaceStatus': "'up'", 'axInterfaceMediaActiveSpeed': '10000',
                    'axInterfaceAlias': '', 'axInterfaceMacAddr': '52:54:00:07:27:fb',
                    'axInterfaceFlowCtrlOperStatus': "'false'"}},
            ('IP-MIB', 'ipAddrTable'): {
                '192.168.122.111': {'ipAdEntAddr': '192.168.122.111', 'ipAdEntIfIndex': '0',
                                    'suffix': '192.168.122.111', 'ipAdEntNetMask': '255.255.255.0',
                                    'ipAdEntBcastAddr': '1', 'ipAdEntReasmMaxSize': '65535'},
                '192.168.136.102': {'ipAdEntAddr': '192.168.136.102', 'ipAdEntIfIndex': '2',
                                    'suffix': '192.168.136.102', 'ipAdEntNetMask': '255.255.255.0',
                                    'ipAdEntBcastAddr': '1', 'ipAdEntReasmMaxSize': '65535'},
                '192.168.90.102': {'ipAdEntAddr': '192.168.90.102', 'ipAdEntIfIndex': '4',
                                   'suffix': '192.168.90.102', 'ipAdEntNetMask': '255.255.255.0',
                                   'ipAdEntBcastAddr': '1', 'ipAdEntReasmMaxSize': '65535'}},
            ('IPV6-MIB', 'ipv6AddrPfxLength'): {
                '2.16.225.1.0.0.0.0.0.0.0.0.0.0.0.0.17.18': {
                    'ipv6AddrPfxLength': '64',
                    'suffix': '2.16.225.1.0.0.0.0.0.0.0.0.0.0.0.0.17.18'}},
            ('A10-AX-MIB', 'axTrunkTable'): {
                '1.53': {'axTrunkTypeLacpEnabled': "'false'", 'suffix': '1.53',
                         'axTrunkDescription': 'Trunk 5', 'axTrunkName': '5',
                         'axTrunkPortThreshold': '0', 'axTrunkStatus': "'down'",
                         'axTrunkCfgMemberCount': '1', 'axTrunkPortThresholdTimer': '0'}},
            ('A10-AX-MIB', 'axTrunkCfgMemberTable'): {
                '1.53.1.50': {'axTrunkCfgMemberTrunkName': '5', 'axTrunkCfgMemberName': '2',
                              'suffix': '1.53.1.50', 'axTrunkCfgMemberOperStatus': "'down'",
                              'axTrunkCfgMemberAdminStatus': "'enabled'"}},
            ('A10-AX-MIB', 'axPowerSupplyStatus'): {
                1: {'axPowerSupplyStatus': "'absent'", 'suffix': '1'},
                2: {'axPowerSupplyStatus': "'on'", 'suffix': '2'}},
            ('LLDP-MIB', 'lldpRemSysName'): {},
            ('LLDP-MIB', 'lldpLocPortDesc'): {},
        }

        snmp_mock().get_property.side_effect = lambda *args: property_map[args]
        snmp_mock().get_table.side_effect = lambda *args: table_map[args]

        details = self.runner.discover()

        contact_name = sys_name = location = model = os_version = None
        for attr in details.attributes:
            if attr.relative_address == '':
                if attr.attribute_name == 'Contact Name':
                    contact_name = attr.attribute_value
                elif attr.attribute_name == 'System Name':
                    sys_name = attr.attribute_value
                elif attr.attribute_name == 'Location':
                    location = attr.attribute_value
                elif attr.attribute_name == 'Model':
                    model = attr.attribute_value
                elif attr.attribute_name == 'OS Version':
                    os_version = attr.attribute_value

        self.assertEqual('admin', contact_name)
        self.assertEqual('A10', sys_name)
        self.assertEqual('somewhere', location)
        self.assertEqual('A10AX.13', model)
        self.assertEqual('4.1.0-P10', os_version)

        ports = []
        power_ports = []
        port_channels = []
        chassis = None

        for resource in details.resources:
            if resource.model == 'GenericPort':
                ports.append(resource)
            elif resource.model == 'GenericChassis':
                chassis = resource
            elif resource.model == 'GenericPowerPort':
                power_ports.append(resource)
            elif resource.model == 'GenericPortChannel':
                port_channels.append(resource)

        ports.sort(key=lambda p: p.name)
        power_ports.sort(key=lambda pw: pw.name)
        port_channels.sort(key=lambda pc: pc.name)

        self.assertEqual('Chassis 0', chassis.name)

        expected_port_names = ['Ethernet 1', 'Ethernet 2', 'Ethernet 3', 'Ethernet 4']
        self.assertListEqual([port.name for port in ports], sorted(expected_port_names))

        expected_power_port_names = ['PP2']
        self.assertListEqual([pw.name for pw in power_ports], sorted(expected_power_port_names))

        expected_port_channel_names = ['PC5']
        self.assertListEqual([pc.name for pc in port_channels], sorted(expected_port_channel_names))

    @patch('cloudshell.devices.snmp_handler.QualiSnmp')
    def test_not_supported_os(self, snmp_mock):
        property_map = {
            ('SNMPv2-MIB', 'sysDescr', '0'): 'Cisco IOS',
        }
        snmp_mock().get_property.side_effect = lambda *args: property_map[args]

        self.assertRaisesRegexp(
            A10Exception,
            '^Unsupported device OS$',
            self.runner.discover,
        )

    @patch('cloudshell.devices.snmp_handler.QualiSnmp')
    def test_wrong_os_version_and_model(self, snmp_mock):
        property_map = {
            ('SNMPv2-MIB', 'sysDescr', '0'):
                'Thunder Series Unified Application Service Gateway vThunder, ACOS ',
            ('SNMPv2-MIB', 'sysContact', '0'): 'admin',
            ('SNMPv2-MIB', 'sysName', '0'): 'A10',
            ('SNMPv2-MIB', 'sysLocation', '0'): 'somewhere',
            ('SNMPv2-MIB', 'sysObjectID', '0'): 'A10-COMMON-MIB::',
            ('A10-AX-MIB', 'axSysSerialNumber', 0): '12345678',
        }
        table_map = {
            ('A10-AX-MIB', 'axInterfaceTable'): {},
            ('IP-MIB', 'ipAddrTable'): {},
            ('IPV6-MIB', 'ipv6AddrPfxLength'): {},
            ('A10-AX-MIB', 'axTrunkTable'): {},
            ('A10-AX-MIB', 'axTrunkCfgMemberTable'): {},
            ('A10-AX-MIB', 'axPowerSupplyStatus'): {},
            ('LLDP-MIB', 'lldpRemSysName'): {},
            ('LLDP-MIB', 'lldpLocPortDesc'): {},
        }

        snmp_mock().get_property.side_effect = lambda *args: property_map[args]
        snmp_mock().get_table.side_effect = lambda *args: table_map[args]

        details = self.runner.discover()

        model = os_version = None
        for attr in details.attributes:
            if attr.relative_address == '':
                if attr.attribute_name == 'Model':
                    model = attr.attribute_value
                elif attr.attribute_name == 'OS Version':
                    os_version = attr.attribute_value

        self.assertEqual('', model)
        self.assertEqual('', os_version)

    @patch('cloudshell.devices.snmp_handler.QualiSnmp')
    def test_adjacent(self, snmp_mock):
        property_map = {
            ('SNMPv2-MIB', 'sysDescr', '0'):
                'Thunder Series Unified Application Service Gateway vThunder, ACOS 4.1.0-P10,',
            ('SNMPv2-MIB', 'sysContact', '0'): 'admin',
            ('SNMPv2-MIB', 'sysName', '0'): 'A10',
            ('SNMPv2-MIB', 'sysLocation', '0'): 'somewhere',
            ('SNMPv2-MIB', 'sysObjectID', '0'): 'A10-COMMON-MIB::a10AX.13',
            ('A10-AX-MIB', 'axSysSerialNumber', 0): '12345678',
            ('IF-MIB', 'ifType', 1): "'ethernetCsmacd'",
            ('LLDP-MIB', 'lldpRemPortDesc', '12.50.1.12'): 'Ethernet 12'
        }
        table_map = {
            ('A10-AX-MIB', 'axInterfaceTable'): {
                1: {'axInterfaceMediaMaxSpeed': '10000', 'suffix': '1',
                    'axInterfaceAdminStatus': "'true'", 'axInterfaceIndex': '1',
                    'axInterfaceMediaMaxDuplex': "'auto'",
                    'axInterfaceFlowCtrlAdminStatus': "'disabled'", 'axInterfaceMtu': '1500',
                    'axInterfaceMediaActiveDuplex': "'full'", 'axInterfaceName': 'Ethernet 1',
                    'axInterfaceStatus': "'up'", 'axInterfaceMediaActiveSpeed': '10000',
                    'axInterfaceAlias': '', 'axInterfaceMacAddr': '52:54:00:97:83:4e',
                    'axInterfaceFlowCtrlOperStatus': "'false'"}},
            ('IP-MIB', 'ipAddrTable'): {},
            ('IPV6-MIB', 'ipv6AddrPfxLength'): {},
            ('A10-AX-MIB', 'axTrunkTable'): {},
            ('A10-AX-MIB', 'axTrunkCfgMemberTable'): {},
            ('A10-AX-MIB', 'axPowerSupplyStatus'): {},
            ('LLDP-MIB', 'lldpRemSysName'): {
                '12.50.1.12': {'lldpRemSysName': 'Other_device'}},
            ('LLDP-MIB', 'lldpLocPortDesc'): {
                '50.1': {'lldpLocPortDesc': 'Ethernet 1'}},
        }

        snmp_mock().get_property.side_effect = lambda *args: property_map[args]
        snmp_mock().get_table.side_effect = lambda *args: table_map[args]

        self.runner.discover()
