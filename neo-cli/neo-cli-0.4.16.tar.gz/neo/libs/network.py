from neo.libs import login as login_lib
from neutronclient.v2_0 import client as neutron_client


def get_neutron_client():
    neutron = neutron_client.Client(session=login_lib.get_session())
    return neutron


def get_list():
    neutron = get_neutron_client()
    networks = neutron.list_networks()
    return networks['networks']


def do_delete(network_id):
    neutron = get_neutron_client()
    neutron.delete_network(network_id)
