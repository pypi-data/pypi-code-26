import json
import os
from random import randint
import ipaddress
from time import sleep


def get_receipt(skale, tx):
    return skale.web3.eth.getTransactionReceipt(tx)


def await_receipt(skale, tx, retries=10, timeout=5):
    for _ in range(0, retries):
        receipt = get_receipt(skale, tx)
        if (receipt != None):
            return receipt
        sleep(timeout)
    return None


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
