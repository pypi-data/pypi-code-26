import json
import os
from random import randint
import ipaddress


def check_port(port):
    if port not in range(1, 65535):
        raise ValueError(f'{port} does not appear to be a valid port. Allowed range: 1-65535')


def check_ip(ip):
    return ipaddress.ip_address(ip)


def generate_ws_addr(ip, port):
    check_ip(ip)
    check_port(port)
    return 'ws://' + ip + ':' + str(port)


def get_default_abipath():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    abi_dir = os.path.join(current_dir, os.pardir)
    return os.path.join(abi_dir, 'contracts_data.json')


def get_abi(abi_filepath=None):
    if not abi_filepath:
        abi_filepath = get_default_abipath()
    with open(abi_filepath) as data_file:
        data = json.load(data_file)
    return data


def generate_nonce():
    return randint(0, 65534)
