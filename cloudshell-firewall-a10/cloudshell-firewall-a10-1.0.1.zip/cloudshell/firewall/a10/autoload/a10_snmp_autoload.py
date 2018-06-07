import os
import re

import ipaddress
from cloudshell.devices.autoload.autoload_builder import AutoloadDetailsBuilder, AutoLoadDetails
from cloudshell.devices.standards.firewall.autoload_structure import GenericResource, \
    GenericChassis, GenericPort, GenericPortChannel, GenericPowerPort

from cloudshell.firewall.a10.helpers.exceptions import A10Exception


class A10SNMPAutoload(object):
    VENDOR = 'A10'

    def __init__(self, snmp_service, shell_name, shell_type, resource_name, logger):
        """Basic init with injected snmp handler and logger"""

        self.snmp_service = snmp_service
        self.shell_name = shell_name
        self.shell_type = shell_type
        self.resource_name = resource_name
        self.logger = logger

        self.chassis = None
        self.resource = GenericResource(shell_name, resource_name, resource_name, shell_type)

    def discover(self, supported_os):
        """General entry point for autoload,
            read device structure and attributes: chassis, ports, port-channels and power supplies

        :return: AutoLoadDetails object
        :rtype: AutoLoadDetails
        """

        if not self._is_valid_device_os(supported_os):
            raise A10Exception('Unsupported device OS')

        self.logger.info('*' * 70)
        self.logger.info('Start SNMP discovery process .....')

        self._load_mibs()
        self.snmp_service.load_mib(['A10-COMMON-MIB', 'A10-AX-MIB'])
        self._get_device_details()

        self._load_snmp_tables()
        self._add_chassis()
        self._add_ports()
        self._add_power_ports()
        self._add_port_channels()

        autoload_details = AutoloadDetailsBuilder(self.resource).autoload_details()
        self._log_autoload_details(autoload_details)
        return autoload_details

    def _load_mibs(self):
        """Loads A10 specific mibs inside snmp handler"""

        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mibs'))
        self.snmp_service.update_mib_sources(path)

    def _load_snmp_tables(self):
        """Load all A10 required snmp tables"""

        self.logger.info('Start loading MIB tables:')

        self.if_table = self.snmp_service.get_table('A10-AX-MIB', 'axInterfaceTable')
        self.ip_v4_table = self.snmp_service.get_table('IP-MIB', 'ipAddrTable')
        self.ip_v6_table = self.snmp_service.get_table('IPV6-MIB', 'ipv6AddrPfxLength')
        self.port_channel_table = self.snmp_service.get_table('A10-AX-MIB', 'axTrunkTable')
        self.port_channel_member_table = self.snmp_service.get_table(
            'A10-AX-MIB', 'axTrunkCfgMemberTable')
        self.power_ports = self.snmp_service.get_table('A10-AX-MIB', 'axPowerSupplyStatus')
        self.lldp_remote_table = self.snmp_service.get_table('LLDP-MIB', 'lldpRemSysName')
        self.lldp_local_table = {v['lldpLocPortDesc']: k for k, v in self.snmp_service.get_table(
            'LLDP-MIB', 'lldpLocPortDesc').iteritems()}

        self.logger.info('MIB Tables loaded successfully')

    def _get_unique_id(self, obj_type, id_):
        return '{}.{}.{}'.format(self.resource_name, obj_type, id_)

    def _add_chassis(self):
        self.logger.info('Building Chassis')

        id_ = 0
        unique_id = self._get_unique_id('chassis', id_)
        chassis_obj = GenericChassis(self.shell_name, 'Chassis {}'.format(id_), unique_id)
        chassis_obj.model = ''
        chassis_obj.serial_number = self.snmp_service.get_property(
            'A10-AX-MIB', 'axSysSerialNumber', 0)

        self.resource.add_sub_resource(id_, chassis_obj)
        self.chassis = chassis_obj

        self.logger.info('Building Chassis completed')

    def _add_ports(self):
        self.logger.info('Loading Ports')

        for id_, attrs in self.if_table.items():
            attrs['ifType'] = self.snmp_service.get_property('IF-MIB', 'ifType', id_)

            unique_id = self._get_unique_id('port', id_)
            port_obj = GenericPort(self.shell_name, attrs['axInterfaceName'], unique_id)
            port_obj.port_description = attrs['axInterfaceAlias']
            port_obj.l2_protocol_type = attrs['ifType'].replace('\'', '')
            port_obj.mac_address = attrs['axInterfaceMacAddr']
            port_obj.mtu = int(attrs['axInterfaceMtu'])
            port_obj.bandwidth = int(attrs['axInterfaceMediaMaxSpeed'])
            port_obj.ipv4_address = self._get_ipv4_interface_address(id_)
            port_obj.ipv6_address = self._get_ipv6_interface_address(id_)
            port_obj.duplex = self._get_port_duplex(id_)
            port_obj.auto_negotiation = self._get_port_auto_negotiation(id_)
            port_obj.adjacent = self._get_adjacent(attrs['axInterfaceName'])

            self.chassis.add_sub_resource(id_, port_obj)
            self.logger.info('Added {} Port'.format(attrs['axInterfaceName']))

        self.logger.info('Building Ports completed')

    def _get_port_duplex(self, port_id):
        if self.if_table[port_id]['axInterfaceMediaActiveDuplex'] != "'full'":
                return 'Half'
        return 'Full'

    def _get_port_auto_negotiation(self, port_id):
        return self.if_table[port_id]['axInterfaceFlowCtrlAdminStatus'] == "'enabled'"

    def _add_power_ports(self):
        self.logger.info('Building PowerPorts')

        for id_, attrs in self.power_ports.iteritems():
            if attrs['axPowerSupplyStatus'] != "'absent'":
                unique_id = self._get_unique_id('power-port', id_)
                power_port = GenericPowerPort(self.shell_name, 'PP{}'.format(id_), unique_id)
                power_port.model = ''
                power_port.port_description = ''
                power_port.version = ''
                power_port.serial_number = ''

                self.chassis.add_sub_resource(id_, power_port)
                self.logger.info('Added PP{} Power Port'.format(id_))

        self.logger.info('Building Power Ports completed')

    def _add_port_channels(self):
        self.logger.info('Building Port Channels')

        for id_, attrs in self.port_channel_table.iteritems():
            name = attrs['axTrunkName']
            id_ = int(name)
            unique_id = self._get_unique_id('port_channel', id_)
            member_ids = [v['axTrunkCfgMemberName'] for v in self.port_channel_member_table.values()
                          if v['axTrunkCfgMemberTrunkName'] == name]
            member_names = [self.if_table[int(if_id)]['axInterfaceName'] for if_id in member_ids]

            port_channel = GenericPortChannel(self.shell_name, 'PC{}'.format(name), unique_id)
            port_channel.port_description = attrs['axTrunkDescription']
            port_channel.associated_ports = '; '.join(member_names)
            port_channel.ipv4_address = next(iter(
                filter(None, map(self._get_ipv4_interface_address, member_ids))), '')
            port_channel.ipv6_address = next(iter(
                filter(None, map(self._get_ipv6_interface_address, member_ids))), '')

            self.resource.add_sub_resource(id_, port_channel)
            self.logger.info('Added {} Port Channel'.format(name))

        self.logger.info('Building Port Channels completed')

    def _log_autoload_details(self, autoload_details):
        """Logging autoload details

        :param autoload_details:
        """

        self.logger.debug('-------------------- <RESOURCES> ----------------------')
        for resource in autoload_details.resources:
            self.logger.debug(
                '{0:15}, {1:20}, {2}'.format(resource.relative_address, resource.name,
                                             resource.unique_identifier))
        self.logger.debug('-------------------- </RESOURCES> ----------------------')

        self.logger.debug('-------------------- <ATTRIBUTES> ---------------------')
        for attribute in autoload_details.attributes:
            self.logger.debug('-- {0:15}, {1:60}, {2}'.format(attribute.relative_address,
                                                              attribute.attribute_name,
                                                              attribute.attribute_value))
        self.logger.debug('-------------------- </ATTRIBUTES> ---------------------')

    def _is_valid_device_os(self, supported_os):
        """Validate device OS using snmp

        :rtype: bool
        :return: True or False
        """

        system_description = self.snmp_service.get_property('SNMPv2-MIB', 'sysDescr', '0')
        self.logger.debug('Detected system description: \'{0}\''.format(system_description))

        result = re.search(
            r'\s({0})\s'.format('|'.join(supported_os)),
            system_description,
            flags=re.DOTALL | re.IGNORECASE)

        if result:
            return True
        else:
            error_message = 'Incompatible driver! Please use this driver for "{0}" ' \
                            'operation system(s)'.format(str(tuple(supported_os)))
            self.logger.error(error_message)
            return False

    def _get_ipv4_interface_address(self, port_id):
        """Get IPv4 address details for provided port"""

        for ip, attrs in self.ip_v4_table.iteritems():
            if str(attrs.get('ipAdEntIfIndex')) == str(port_id):
                return ip

    def _get_ipv6_interface_address(self, port_id):
        """Get IPv6 address details for provided port"""

        for key, _ in self.ip_v6_table.iteritems():
            ints = map(int, key.split('.'))
            id_, addr = ints[0], ints[2:]
            if str(id_) == str(port_id):
                addr = ((u'{:02x}{:02x}:' * 8)[:-1]).format(*addr)
                return str(ipaddress.IPv6Address(addr))

    def _get_device_details(self):
        """ Get root element attributes """

        self.logger.info('Building Root')

        self.resource.contact_name = self.snmp_service.get_property('SNMPv2-MIB', 'sysContact', '0')
        self.resource.system_name = self.snmp_service.get_property('SNMPv2-MIB', 'sysName', '0')
        self.resource.location = self.snmp_service.get_property('SNMPv2-MIB', 'sysLocation', '0')
        self.resource.vendor = self.VENDOR
        self.resource.os_version = self._get_device_os_version()
        self.resource.model = self._get_device_model()

    def _get_device_os_version(self):
        """ Determine device OS version using SNMP """

        system_description = self.snmp_service.get_property('SNMPv2-MIB', 'sysDescr', '0')
        match = re.search(r'ACOS (?P<version>\S+)', system_description, re.IGNORECASE)

        try:
            result = match.groupdict()['version'].rstrip(',')
        except (AttributeError, KeyError):
            result = ''

        return result

    def _get_device_model(self):
        """Get device model from snmp SNMPv2 mib

        :return: device model
        :rtype: str
        """

        output = self.snmp_service.get_property('SNMPv2-MIB', 'sysObjectID', '0')
        match = re.search(r'::(?P<model>\S+$)', output)

        try:
            result = match.groupdict()['model'].upper()
        except (AttributeError, KeyError):
            result = ''

        return result

    def _get_adjacent(self, interface_name):
        """Get connected device interface and device name to the specified port
            using lldp protocol

        :param interface_name:
        :return: device's name and port connected to port id
        :rtype: str
        """

        result_template = '{remote_host} through {remote_port}'
        result = ''
        if self.lldp_local_table:
            key = self.lldp_local_table.get(interface_name, None)
            if key:
                for port_id, rem_table in self.lldp_remote_table.iteritems():
                    if '.{0}.'.format(key) in port_id:
                        remoute_sys_name = rem_table.get('lldpRemSysName', '')
                        remoute_port_name = self.snmp_service.get_property(
                            'LLDP-MIB', 'lldpRemPortDesc', port_id)
                        if remoute_port_name and remoute_sys_name:
                            result = result_template.format(remote_host=remoute_sys_name,
                                                            remote_port=remoute_port_name)
                            break
        return result
