from cloudcix.client import Client


class iaas:
    """
    Description
    """
    _application_name = 'DNS'

    aggregated_blacklist = Client(
        application=_application_name,
        service_uri='AggregatedBlacklist/'
    )
    allocation = Client(
        application=_application_name,
        service_uri='Allocation/'
    )
    asn = Client(
        application=_application_name,
        service_uri='ASN/'
    )
    blacklist = Client(
        application=_application_name,
        service_uri='CIXBlacklist/'
    )
    blacklist_source = Client(
        application=_application_name,
        service_uri='BlacklistSource/'
    )
    cloud = Client(
        application=_application_name,
        service_url='Cloud/'
    )
    domain = Client(
        application=_application_name,
        service_uri='Domain/'
    )
    hypervisor = Client(
        application=_application_name,
        service_uri='Hypervisor/'
    )
    image = Client(
        application=_application_name,
        service_uri='Image/'
    )
    ipmi = Client(
        application=_application_name,
        service_uri='IPMI/'
    )
    ipaddress = Client(
        application=_application_name,
        service_uri='IPAddress/'
    )
    ip_validator = Client(
        application=_application_name,
        service_uri='IPValidator/'
    )
    location_hasher = Client(
        application=_application_name,
        service_uri='LocationHasher/'
    )
    nmap = Client(
        application=_application_name,
        service_uri='nmap/'
    )
    pool_ip = Client(
        application=_application_name,
        service_uri='PoolIP/'
    )
    project = Client(
        application=_application_name,
        service_uri='Project/'
    )
    record = Client(
        application=_application_name,
        service_uri='Record/'
    )
    recordptr = Client(
        application=_application_name,
        service_uri='RecordPTR/'
    )
    router = Client(
        application=_application_name,
        service_uri='Router/'
    )
    subnet = Client(
        application=_application_name,
        service_uri='Subnet/'
    )
    subnet_space = Client(
        application=_application_name,
        service_uri='Allocation/{idAllocation}/Subnet_space/'
    )
    vm = Client(
        application=_application_name,
        service_uri='VM/'
    )
    vm_history = Client(
        application=_application_name,
        service_uri="VMHistory/"
    )
    vpn_tunnel = Client(
        application=_application_name,
        service_uri="VPNTunnel/"
    )
    vrf = Client(
        application=_application_name,
        service_uri='VRF/'
    )
    whitelist = Client(
        application=_application_name,
        service_uri='CIXWhitelist/'
    )
    server = Client(
        application=_application_name,
        service_uri='Server/'
    )
    macaddress = Client(
        application=_application_name,
        service_uri='MacAddress/'
    )
