from cloudshell.cli.command_template.command_template import CommandTemplate


ENABLE_SNMP_SERVER = CommandTemplate('snmp-server enable service')
EXIT_MODE = CommandTemplate('exit')

SNMP_GET_CONFIG = CommandTemplate('show running-config snmp-server')

# SNMP v2
SNMP_V2_CREATE_REMOVE_USER = CommandTemplate('[no {remove}]snmp-server SNMPv1-v2c user {user}')
SNMP_V2_CREATE_COMMUNITY = CommandTemplate('community read {community}')

# SNMP v3
SNMP_V3_CREATE_REMOVE_VIEW = CommandTemplate('[no {remove}]snmp-server view {view} 1 included')
SNMP_V3_CREATE_REMOVE_GROUP = CommandTemplate(
    '[no {remove}]snmp-server group {group} v3 {security_level} read {view}')
SNMP_V3_CREATE_REMOVE_USER = CommandTemplate(
    '[no {remove}]snmp-server SNMPv3 user {user} group {group} v3 '
    '[no{no_security}]auth [{auth_type} {password}]'  # md5|sha
    '[ priv {priv_type} {priv_key}]')  # aes|des
