# -*- coding: utf-8 -*-
'''
Created on Oct 17, 2016

@author: davidlepage
'''
import logging
from smc import session
from smc.core.engine import Engine
from smc.elements.servers import LogServer
from smc.base.collection import Search
from smc.core.sub_interfaces import ClusterVirtualInterface
from smc.core.interfaces import ClusterPhysicalInterface, TunnelInterface, Layer3PhysicalInterface
from smc.administration.user_auth.users import InternalUserDomain
from smc.routing.access_list import IPAccessList
from smc.routing.route_map import RouteMap



logger = logging.getLogger(__name__)


def get_options_for_link(link):
    r = session.session.options(link)  # @UndefinedVariable
    headers = r.headers['allow']
    allowed = []
    if headers:
        for header in headers.split(','):
            if header.replace(' ', '') != 'OPTIONS':
                allowed.append(header)
    return allowed

def head_request(link):
    r = session.session.head(link)  # @UndefinedVariable
    print(vars(r))


if __name__ == '__main__':
    import sys
    import time
    from pprint import pprint
    start_time = time.time()
    
    
    #from requests_toolbelt import SSLAdapter
    #import requests
    #import ssl
    
    #s = requests.Session()
    #s.mount('https://', SSLAdapter(ssl.PROTOCOL_TLSv1))
    #session.set_file_logger(log_level=10, path='/Users/davidlepage/Downloads/smc-test.log')
    #session.set_stream_logger(log_level=logging.DEBUG)
    #session.set_stream_logger(log_level=logging.DEBUG, logger_name='urllib3')
    
    logging.getLogger()
    logging.basicConfig(
        level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s.%(funcName)s: %(message)s')
    
    #session.login(url='http://172.18.1.36:8082', api_key='kN8CYwTrxB9UNLPyTcnX0001',
    #              api_version='5.10')
    
    session.login(url='https://172.18.1.151:8082', api_key='dUgAvLDB2tAmiSMSkyxfCZaq',
                  verify=False, beta=True, timeout=30, retry_on_busy=True)
    
    
    #session.login(url='https://172.18.1.151:8082', login='dlepage3', pwd='1970keegan', verify=False)
    #session.login(url='http://172.18.1.26:8082', api_key='kKphtsbQKjjfHR7amodA0001', timeout=45, beta=True)
    
    #session.login(url='http://172.18.1.150:8082', api_key='EiGpKD4QxlLJ25dbBEp20001', timeout=30,
    #              verify=False, beta=True)
    
    #session.login(url='https://cheryl.gallant.lab.go4labs.net:8082', api_key='zPC68FFnivs2FCMnjDQtSUEK', verify=False)
    #engine = Engine('sg_vm')
    
    
    from smc.vpn.policy import GatewayNode
    from smc.vpn.policy import PolicyVPN
    from smc.base.model import Element
    
    engine = Engine('myfw4')
    for mapping in engine.vpn_mappings:
        print(mapping._central_gateway)
        
        internal_gw = engine.vpn.internal_gateway
        vpn = PolicyVPN('myvpn')
        vpn.open()
        gn = GatewayNode(href=mapping._central_gateway)
        gn.delete()
        vpn.save()  
        vpn.close()
        
    
#     ed = engine.data
#     for attr in ('link', 'physicalInterfaces', 'dynamic_routing', 'nodes',
#                  'snmp_agent_ref', 'snmp_interface', 'snmp_location', 'key',
#                  'location_ref', 'gateway_settings_ref', 'log_server_ref',
#                  'antivirus'):
#         ed.pop(attr, None)
#          
#      
#     pprint(vars(ed))
    
#     for permission in engine.permissions:
#         print(permission)
#     
#     from smc.elements.user import AdminUser
#     admin = AdminUser('testadmin')
#     pprint(vars(admin.data))
    
    
    
        
    
    # TODO: Change MTU on VLAN
    # Need to create __getattr__ and redirect these lookups
    # to self._parent as well as other methods
    
    

    session.logout()
    sys.exit(1)
    
    
    def extract_nat_details(d, expand=False):
        _nat_details = {}
        if d.get('translation_values', []):
            d['translated_value'] = d.pop('translation_values', {})[0]
    
    def to_yaml(rule, expand=None):
        _rule = {
            'name': rule.name, 'tag': rule.tag,
            'is_disabled': rule.is_disabled,
            'comment': rule.comment}
        
        _rule.update(used_on=rule.used_on.name)
        
        for field in ('sources', 'destinations', 'services'):
            if getattr(rule, field).is_any:
                _rule[field] = {'any': True}
            elif getattr(rule, field).is_none:
                _rule[field] = {'none': True}
            else:
                if expand and field in expand:
                    tmp = {}
                    for entry in getattr(rule, field).all():
                        element_type = entry.typeof
                        if entry.typeof in engine_type:
                            element_type = 'engine'
                        elif 'alias' in entry.typeof:
                            element_type = 'alias'
                        tmp.setdefault(element_type, []).append(
                            entry.name)
                else:
                    tmp = getattr(rule, field).all_as_href()
                _rule[field] = tmp
        
        for nat in ('dynamic_src_nat', 'static_src_nat', 'static_dst_nat'):
            if getattr(rule, nat).has_nat:
                #_rule[nat] = getattr(rule, nat, {}).data.get(nat)
                _rule[nat] = extract_nat_details(
                    getattr(rule, nat, {}).data.get(nat))
        
        return _rule
    
    from smc.policy.layer3 import FirewallPolicy
    
    p = FirewallPolicy('TestPolicy3')
    
    #for x in p.fw_ipv4_nat_rules:
    #    pprint(to_yaml(x))
    
    engine = Engine('myfw3')

    
#     element, updated, created = OSPFProfile.update_or_create(with_status=True, **ospf)
#     print("updated: %s, created: %s" % (updated, created))
    
    def area_to_yaml(area):
        yaml = {}
        yaml.update(
            name=area.name,
            comment=area.comment,
            area_type=area.area_type,
            interface_settings_ref=area.interface_settings_ref.name)
        
        for filt in ('inbound_filters', 'outbound_filters'):
            if len(getattr(area, '%s_ref' % filt)):
                for _filt in getattr(area, filt):
                    _filter = {_filt.typeof: [_filt.name]}
                    yaml.setdefault(filt, {}).update(_filter)
                
        return yaml
    
    def profile_to_yaml(profile):
        yaml = {}
        yaml.update(
            name=profile.name,
            comment=profile.comment,
            external_distance=profile.external_distance,
            inter_distance=profile.inter_distance,
            intra_distance=profile.intra_distance,
            domain_settings_ref=profile.domain_settings_ref.name,
            default_metric=profile.data.get('default_metric', None)
            )
        redist_entries = []
        for redist in profile.data.get('redistribution_entry', []):
            filter_type = redist.pop('filter_type', 'none')
            if filter_type != 'none':
                if filter_type == 'route_map_policy':
                    redist.update(
                        filter={'route_map': [RouteMap.from_href(
                            redist.pop('redistribution_rm_ref')).name]})
                elif filter_type == 'access_list':
                    redist.update(
                        filter={'ip_access_list': [IPAccessList.from_href(
                            redist.pop('redistribution_filter_ref')).name]})
            redist_entries.append(redist)
        yaml.update(redistribution_entry=redist_entries)
        return yaml
    
    
    
    #pprint(get_ospf(engine))
    #pprint(get_bgp(engine))
        
    session.logout()
    sys.exit(1)    
    class custom_setter(object):
        def __init__(self, func, doc=None):
            self.func = func
            self.__doc__ = doc if doc is not None else func.__doc__
        def __set__(self, obj, value):
            return self.func(obj, value)

    
    class element_list(object):
        def __init__(self, attr, doc=None):
            self.attr = attr
        def __set__(self, obj, value):
            elements = [element_resolver(elem) for elem in value]
            obj.data[self.attr] = elements
            return elements
        def __get__(self, obj, owner):
            return [obj.from_href(elem) for elem in obj.data.get(self.attr)]
            
    sentinel = object()
    
    import yaml  # @UnresolvedImport
    from smc.elements.network import Zone
    
    def zone_finder(zones, zone):
        for z in zones:
            if z.href == zone:
                return z.name
    
    from smc.vpn.policy import PolicyVPN
    def get_policy_vpn(engine):
        vpn_mappings = engine.vpn_mappings
        engine_internal_gw = engine.vpn.internal_gateway.name
        policy_vpn = []
        _seen = []
        if vpn_mappings:
            for mapping in vpn_mappings:
                mapped_vpn = mapping.vpn
                if mapped_vpn.name not in _seen:
                    _vpn = {'name': mapped_vpn.name}
                    vpn = PolicyVPN(mapped_vpn.name)
                    vpn.open()
                    nodes = vpn.central_gateway_node
                    node_central = nodes.get_contains(engine_internal_gw)
                    _vpn.update(central_node=True if node_central else False)
                    if not node_central: # If it's a central node it can't be a satellite node
                        nodes = vpn.satellite_gateway_node
                        _vpn.update(satellite_node=True if nodes.get_contains(engine_internal_gw) else False)
                    else:
                        _vpn.update(satellite_node=False)
                    if vpn.mobile_vpn_topology != 'None':
                        mobile_node = vpn.mobile_gateway_node
                        _vpn.update(mobile_gateway=True if mobile_node.get_contains(engine_internal_gw) else False)
                    
                    policy_vpn.append(_vpn)
                    vpn.close()
                    _seen.append(mapped_vpn.name)
        return policy_vpn
    
    
    engine = Engine('newcluster')
    print(get_policy_vpn(engine))
    session.logout()
    
    sys.exit(1)
    def yaml_cluster(engine):
        """
        Example interface dict created from cluster engine:
            
        
        Nodes dict key will always have at least `address`,
        `network_value` and `nodeid` if the interface definition
        has interface addresses assigned.
        """
        # Prefetch all zones to reduce queries
        zone_cache = list(Zone.objects.all())
        management = ('primary_mgt', 'backup_mgt', 'primary_heartbeat')
        yaml_engine = {'name': engine.name, 'type': engine.type}
        interfaces = []
        
        for interface in engine.interface:
            if not isinstance(interface, 
                (ClusterPhysicalInterface, Layer3PhysicalInterface, TunnelInterface)):
                continue
            top_itf = {}
            
            # Interface common settings
            top_itf.update(interface_id=interface.interface_id)
            
            if getattr(interface, 'macaddress', None) is not None:
                top_itf.update(macaddress=interface.macaddress)
            if getattr(interface, 'comment', None):
                top_itf.update(comment=interface.comment)
            if interface.zone_ref:
                top_itf.update(zone_ref=zone_finder(
                    zone_cache, interface.zone_ref))
            
            cvi_mode = getattr(interface, 'cvi_mode', None)
            if cvi_mode is not None and cvi_mode != 'none':
                top_itf.update(cvi_mode=interface.cvi_mode)
            
            if 'physical_interface' not in interface.typeof:
                top_itf.update(type=interface.typeof)
            
            if interface.has_interfaces:
                _interfaces = []    
                nodes = {}
                for sub_interface in interface.all_interfaces:
                    node = {}
                    if isinstance(sub_interface, ClusterVirtualInterface):
                        nodes.update(
                            cluster_virtual=sub_interface.address,
                            network_value=sub_interface.network_value)

                        # Skip remaining to get nodes
                        continue
                    else: # NDI
                        if getattr(sub_interface, 'dynamic', None):
                            node.update(dynamic=True, dynamic_index=
                                getattr(sub_interface, 'dynamic_index', 0))
                        else:
                            node.update(
                                address=sub_interface.address,
                                network_value=sub_interface.network_value,
                                nodeid=sub_interface.nodeid)
                            
                            for role in management:
                                if getattr(sub_interface, role, None):
                                    yaml_engine[role] = getattr(sub_interface, 'nicid')    

                    nodes.setdefault('nodes', []).append(node)
                
                if nodes:
                    _interfaces.append(nodes)
                if _interfaces:
                    top_itf.update(interfaces=_interfaces)
            
            elif interface.has_vlan:

                for vlan in interface.vlan_interface:
                    
                    itf = {'vlan_id': vlan.vlan_id}
                    if getattr(vlan, 'comment', None):
                        itf.update(comment=vlan.comment)
    
                    _interfaces = []    
                    nodes = {}
                    if vlan.has_interfaces:
                        for sub_vlan in vlan.all_interfaces:
                            node = {}
    
                            if isinstance(sub_vlan, ClusterVirtualInterface):
                                itf.update(
                                    cluster_virtual=sub_vlan.address,
                                    network_value=sub_vlan.network_value)
                                continue
                            else: # NDI
                                # Dynamic address
                                if getattr(sub_vlan, 'dynamic', None):
                                    node.update(dynamic=True, dynamic_index=
                                        getattr(sub_vlan, 'dynamic_index', 0))
                                else:
                                    node.update(
                                        address=sub_vlan.address,
                                        network_value=sub_vlan.network_value,
                                        nodeid=sub_vlan.nodeid)
    
                                for role in management:
                                    if getattr(sub_vlan, role, None):
                                        yaml_engine[role] = getattr(sub_vlan, 'nicid')
                
                            if vlan.zone_ref:
                                itf.update(zone_ref=zone_finder(
                                    zone_cache, vlan.zone_ref))
                            
                            nodes.setdefault('nodes', []).append(node)
                            
                        if nodes:
                            _interfaces.append(nodes)
                        if _interfaces:
                            itf.update(nodes)
                        
                        top_itf.setdefault('interfaces', []).append(itf)
                
                    else:
                        # Empty VLAN, check for zone
                        if vlan.zone_ref:
                            itf.update(zone_ref=zone_finder(
                                zone_cache, vlan.zone_ref))
                        
                        top_itf.setdefault('interfaces', []).append(itf)    
                        
            interfaces.append(top_itf)
            
        yaml_engine.update(
            interfaces=interfaces,
            default_nat=engine.default_nat.status,
            antivirus=engine.antivirus.status,
            file_reputation=engine.file_reputation.status,
            domain_server_address=[dns.value for dns in engine.dns
                                   if dns.element is None])
        if engine.comment:
            yaml_engine.update(comment=engine.comment)
    
        # Only return the location if it is not the default (Not set) location
        location = engine.location
        if location:
            yaml_engine.update(location=location.name)
        # Show SNMP data if SNMP is enabled
        if engine.snmp.status:
            snmp = engine.snmp
            data = dict(snmp_agent=snmp.agent.name)
            if snmp.location:
                data.update(snmp_location=snmp.location)
            interfaces = snmp.interface
            if interfaces:
                data.update(snmp_interface=[itf.interface_id for itf in interfaces])
            yaml_engine.update(snmp=data)
        
        if getattr(engine, 'cluster_mode', None):
            yaml_engine.update(cluster_mode=engine.cluster_mode)
        
        # BGP Data
        bgp = engine.bgp
        data = dict(enabled=bgp.status,
                    router_id=bgp.router_id)
        
        if bgp.status:    
            as_element = bgp.autonomous_system
            autonomous_system=dict(name=as_element.name,
                                   as_number=as_element.as_number,
                                   comment=as_element.comment)
            data.update(autonomous_system=autonomous_system)
            
            bgp_profile = bgp.profile
            if bgp_profile:
                data.update(bgp_profile=bgp_profile.name)
            
            antispoofing_map = {}
            for net in bgp.antispoofing_networks:
                antispoofing_map.setdefault(net.typeof, []).append(
                    net.name)
            antispoofing_network = antispoofing_map if antispoofing_map else {}
            data.update(antispoofing_network=antispoofing_network)
                
            announced_network = []
            for announced in bgp.advertisements:
                element, route_map = announced
                d = {element.typeof: {'name': element.name}}
                if route_map:
                    d[element.typeof].update(route_map=route_map.name)
                announced_network.append(d)
            data.update(announced_network=announced_network)
            
        yaml_engine.update(bgp=data)
        bgp_peering = []
        for interface, network, peering in engine.routing.bgp_peerings:
            peer_data = {}
            peer_data.update(interface_id=interface.nicid,
                             name=peering.name)
            if network:
                peer_data.update(network=network.ip)
            for gateway in peering:
                if gateway.routing_node_element.typeof == 'external_bgp_peer':
                    peer_data.update(external_bgp_peer=gateway.name)
                else:
                    peer_data.update(engine=gateway.name)
            bgp_peering.append(peer_data)
        if bgp_peering:
            data.update(bgp_peering=bgp_peering)
        
        # Netlinks
        netlinks = []
        for netlink in engine.routing.netlinks:
            interface, network, link = netlink
            netlink = {'interface_id': interface.nicid,
                       'name': link.name}
                
            for gw in link:
                gateway = gw.routing_node_element
                netlink.setdefault('destination', []).append(
                    {'name': gateway.name, 'type': gateway.typeof})
            
            netlinks.append(netlink)
        if netlinks:
            yaml_engine.update(netlinks=netlinks)
        
        # Policy VPN mappings
        policy_vpn = get_policy_vpn(engine)
        if policy_vpn:
            yaml_engine.update(policy_vpn=policy_vpn)
        # Lastly, get tags
        tags = [tag.name for tag in engine.categories]
        if tags:
            yaml_engine.update(tags=tags)
        return yaml_engine    

    from smc.vpn.policy import PolicyVPN
    engine = Engine('newcluster')
    #pprint(yaml_cluster(engine))
    
    
    def update_policy_vpn(policy_vpn, engine):
        """
        Update the policy VPN. Provide a list of policy VPN
        dict and update if changed. Policy VPN list of dict
        looks like:
            [{'central_node': True,
              'mobile_gateway': True,
              'name': u'myVPN',
              'satellite_node': False,
              'vpn_profile': u'VPN-A Suite'}]

        :param list policy_vpn: dict of policy VPN
        :param Engine engine: engine reference
        """
        changed = False
        mappings = []
        for mapping in engine.vpn_mappings:
            if mapping.name not in mappings:
                mappings.append(mapping.name)
        
        for vpn in policy_vpn:
            if vpn.get('name') not in mappings:
                _vpn = PolicyVPN(vpn.get('name'))
                _vpn.open()
                if vpn.get('central_node', False):
                    #_vpn.add_central_gateway(engine)
                    pass
                elif vpn.get('satellite_node', False):
                    #_vpn.add_satellite_gateway(engine)
                    pass
                if vpn.get('mobile_gateway', False):
                    _vpn.add_mobile_vpn_gateway(engine)
                _vpn.save()
                _vpn.close()
                changed = True
            else: # Engine is already a member of this VPN
                _vpn = PolicyVPN(vpn.get('name'))
                _vpn.open()
                central = _vpn.central_gateway_node
                print("Central: %s" % central)
                print(vars(central))
                _vpn.save()
                _vpn.close()
            
    
    pvpn = [{'central_node': True,
             'mobile_gateway': False,
             'name': u'ttesst',
             'satellite_node': False}]
    
    from smc.policy.layer3 import FirewallPolicy
    policy = FirewallPolicy('TestPolicy')
    rule = policy.search_rule('@2097170')[0]
    
    
    
    session.logout()
    sys.exit(1)
    class ElementList(object):
        """
        Represents a an element collection that provides the ability
        to add or modify elements. Keeps a cache of the elements fetched
        and removes the ones that are operated on. Typically this is best
        hidden behind a property as it elements in this container will
        require fetching by href to serialize.
        """
        def __init__(self, elementlist):
            self._elements = elementlist
            self._result_cache = None
        
        def _fetch_all(self):
            if self._result_cache is None:
                self._result_cache = [Element.from_href(elem)
                    for elem in self._elements] 

        def __iter__(self):
            self._fetch_all() 
            return iter(self._result_cache) 
        
        def replace_all(self, elements):
            self._elements[:] = elements
        
        def insert(self, elements):
            """
            Insert elements that dont exist
            """
            print("self._elements start: %s" % self._elements)
            self._elements.extend([elem.href for elem
                in elements if elem not in self])
            print("self elem after: %s" % self._elements)
        
        def delete(self, elements):
            """
            Elements to remove if they exist
            """
            self._elements[:] = [elem.href for elem
                in self if elem not in elements]
            if len(self._elements) != len(self._result_cache):
                self._result_cache[:] = [elem for elem in self._result_cache
                    if elem.href in self._elements]
        
          
    from smc.base.structs import NestedDict
    class Foo(NestedDict):
        def __init__(self, data):
            super(Foo, self).__init__(data=data)
        
        @property
        def authentication_options(self):
            return self.get('authentication_options')
            
        @property
        def users(self):
            return ElementList(self.authentication_options.get('users'))
    
    for user in rule.authentication_options.users:
        pprint(vars(user.data))
    foo = InternalUserDomain.get('InternalDomain')
    
    
    #from smc.administration.user_auth.users import InternalUser, InternalUserGroup
    #print(InternalUser.href)
    #foouser = InternalUser.get('cn=foouser,dc=stonegate,domain=InternalDomain123777')
    #print(foouser, foouser.href)
    
    #x = InternalUserGroup.get('cn=myinternalgroup,dc=stonegate,domain=InternalDomain')
    #pprint(vars(x.data))
    
    #y = InternalUserGroup.create(name='testgroup', user_dn='cn=testgroup,dc=stonegate,domain=InternalDomain')
    #print(y)
    
    # TODO: UserElement recurses when trying to instantiate directly
    #y = InternalUserGroup.get('cn=testgroup,dc=stonegate,domain=InternalDomain')
    #pprint(vars(y.data))
    
  
    #u = InternalUser.create(name='fooed4',user_dn='dc=mynewgroup3,domain=InternalDomain')
    #print(u)
    
    session.logout()
    sys.exit(1)
    
    
    #print(ExternalLdapUserDomain('myldapdomain').get_users(['cn=administrator,cn=users,dc=lepages,dc=local']))
    from pprint import pprint
    pprint(vars(foo.data))
    session.logout()
    sys.exit()
        
    print("Methods: %s" % rule.authentication_options.methods)
    print("auth: %s" % rule.authentication_options.require_auth)
    
    for user in rule.authentication_options.users:
        print("user: %s" % user)
        pprint(vars(user.data))
    
    session.logout()
    sys.exit(1)    
    
    #rule.authentication_options.users.append(
    rule.authentication_options.data.setdefault('users', []).append(
        'https://172.18.1.151:8082/6.4/elements/external_ldap_user_group/Y249YWRtaW5pc3RyYXRvcixjbj11c2VycyxkYz1sZXBhZ2VzLGRjPWxvY2FsLGRvbWFpbj1teWxkYXBkb21haW4=')
    
    #print("*** Before update: %s" % rule.authentication_options.users)
    print("******* Updating *********")
    pprint(vars(rule.data))
    rule.update()

        
    from smc.administration.user_auth.users import ExternalLdapUser
    for x in ExternalLdapUser.objects.all():
        print('user: %s' % x)
           
    class UserIDService(Element):
        typeof = 'user_id_service'
    
    class UserIDAgent(Element):
        typeof = 'user_identification_agent'
 
    #ZGM9bGVwYWdlcyxkYz1sb2NhbCxkb21haW49bXlsZGFwZG9tYWlu
    import base64
    code_string = base64.b64decode('ZGM9bGVwYWdlcyxkYz1sb2NhbCxkb21haW49bXlsZGFwZG9tYWlu')
    print('Decoded: %s' % code_string)
    print('Encoded: %s' % base64.b64encode('cn=administrator,cn=users,dc=lepages,dc=local,domain=myldapdomain'))
    
    encoded = base64.b64encode('cn=foobar,dc=lepages,dc=local,domain=myldapdomain')
    print(encoded)
    print("decode foobar: %s" % base64.b64decode('Y249Zm9vYmFyLGRjPWxlcGFnZXMsZGM9bG9jYWwsZG9tYWluPW15bGRhcGRvbWFpbg=='))

    #TODO: BUG in moving rules
#     from smc.policy.layer3 import FirewallPolicy
#     FirewallPolicy('TestPolicy3').delete()
#     policy = FirewallPolicy.get_or_create(name='TestPolicy3')
#     
#     rule = policy.fw_ipv4_access_rules.create(
#             name='foo')
#     policy.fw_ipv4_access_rules.create(name='foo2')
#     rule.update(rank=1.0)
# 
#     # Add a rule only using the MobileVPN
#     policy.fw_ipv4_access_rules.create(
#         name='mobilevpn',
#         sources='any',
#         destinations='any',
#         services='any',
#         action='enforce_vpn',
#         mobile_vpn=True)
#     
#     for x in policy.fw_ipv4_access_rules:
#         pprint(vars(x.data))
# # #  
#     rulesection = policy.fw_ipv4_access_rules.create_rule_section(name='mysection', add_pos=15)
#     foobarred = policy.search_rule('mobilevpn')[0]
#     pprint(vars(foobarred.data))
# #      
#     foobarred.move_rule_after(rulesection)
#     print("After move after")
#     #for num, rules in enumerate(policy.fw_ipv4_access_rules, 1):
#     #    print(num, rules)
# #    
#     for x in policy.fw_ipv4_access_rules:
#         pprint(vars(x.data))
#        
#     foobarred = policy.search_rule('mobilevpn')[0]
#     print("********** DATA AFTER CALLING ?after")
#     pprint(vars(foobarred.data))
# #     
#     rulesection = policy.search_rule('mysection')[0]
#     print("----------------------------------------")       
#     foobarred = policy.search_rule('mobilevpn')[0]
#     pprint(vars(foobarred.data))
#     print("Moving before....")
#     #rulesection = policy.search_rule('myrulesection')[0]
#    
#     foobarred.move_rule_before(rulesection)
#     print("After move after")
#     for num, rules in enumerate(policy.fw_ipv4_access_rules, 1):
#         pprint(vars(rules.data))        
#     foobarred = policy.search_rule('mobilevpn')[0]
    

    vpn = {
            "gateway_nodes_usage": {
                "central_gateway_node_ref": "http://localhost:8082/6.5/elements/vpn/5/gateway_tree_nodes/central/59",
                "satellite_gateway_node_ref": "http://localhost:8082/6.5/elements/vpn/5/gateway_tree_nodes/central/59",
                "mobile_gateway_node_ref": "http://localhost:8082/6.5/elements/vpn/5/gateway_tree_nodes/central/59",
            },
            "gateway_ref": "http://localhost:8082/6.5/elements/fw_cluster/1563/internal_gateway/59",
            "vpn_ref": "http://localhost:8082/6.5/elements/vpn/5"
            }

    session.logout()
    sys.exit(1)
    
    single_fw = {'antivirus': False,
                 'backup_mgt': u'1.2',
                 'bgp': {'bgp_peering': [{'external_bgp_peer': u'bgppeer',
                                          'interface_id': u'1000',
                                          'name': u'mypeering4'}],
                         'enabled': False,
                         'router_id': None},
                 'default_nat': False,
                 'domain_server_address': [u'8.8.8.8'],
                 'file_reputation': False,
                 'interfaces': [{'interface_id': u'15'},
                                {'interface_id': u'1000',
                                 'interfaces': [{'nodes': [{'address': u'90.90.90.71',
                                                            'network_value': u'90.90.90.0/24',
                                                            'nodeid': 1}]}],
                                 'type': 'tunnel_interface'},
                                #{'interface_id': u'6',
                                # 'interfaces': [{'nodes': [{'dynamic': True}]}]},
                                {'interface_id': u'5', 'zone_ref': u'management'},
                                {'interface_id': u'56',
                                 'interfaces': [{'comment': u'added by api',
                                                 'nodes': [{'address': u'56.56.56.56',
                                                            'network_value': u'56.56.56.0/24',
                                                            'nodeid': 1}],
                                                 'vlan_id': u'56'}]},
                                {'interface_id': u'20',
                                 'interfaces': [{'nodes': [{'address': u'11.11.11.11',
                                                            'network_value': u'11.11.11.0/24',
                                                            'nodeid': 1}]}]},
                                {'interface_id': u'SWP_0'},
                                {'interface_id': u'50',
                                 'interfaces': [{'nodes': [{'address': u'50.50.50.1',
                                                            'network_value': u'50.50.50.0/24',
                                                            'nodeid': 1}]}]},
                                {'interface_id': u'49',
                                 'interfaces': [{'nodes': [{'address': u'49.49.49.49',
                                                            'network_value': u'49.49.49.0/24',
                                                            'nodeid': 1}]}]},
                                {'comment': u'foocomment',
                                 'interface_id': u'1008',
                                 'interfaces': [{'nodes': [{'address': u'13.13.13.13',
                                                            'network_value': u'13.13.13.0/24',
                                                            'nodeid': 1}]}],
                                 'type': 'tunnel_interface',
                                 'zone_ref': u'foozone'},
                                {'interface_id': u'4', 'interfaces': [{'vlan_id': u'4'}]},
                                {'interface_id': u'3',
                                 'interfaces': [{'nodes': [{'address': u'4.4.4.5',
                                                            'network_value': u'4.4.4.0/24',
                                                            'nodeid': 1},
                                                           {'address': u'4.4.4.4',
                                                            'network_value': u'4.4.4.0/24',
                                                            'nodeid': 1}]}]},
                                {'interface_id': u'2',
                                 'interfaces': [{'nodes': [{'address': u'12.12.12.10',
                                                            'network_value': u'12.12.12.0/24',
                                                            'nodeid': 1}],
                                                 'vlan_id': u'8',
                                                 'zone_ref': u'foozone'}],
                                 'zone_ref': u'management'},
                                {'interface_id': u'1',
                                 'interfaces': [{'nodes': [{'address': u'2.2.2.2',
                                                            'network_value': u'2.2.2.0/24',
                                                            'nodeid': 1}],
                                                 'vlan_id': u'1'},
                                                {'nodes': [{'address': u'3.3.3.3',
                                                            'network_value': u'3.3.3.0/24',
                                                            'nodeid': 1}],
                                                 'vlan_id': u'2'}]},
                                {'interface_id': u'0',
                                 'interfaces': [{'nodes': [{'address': u'1.1.1.1',
                                                            'network_value': u'1.1.1.0/24',
                                                            'nodeid': 1}]}]},
                                {'interface_id': u'55',
                                 'interfaces': [{'nodes': [{'address': u'55.55.55.55',
                                                            'network_value': u'55.55.55.0/24',
                                                            'nodeid': 1}]}]},
                                {'comment': u'foo',
                                 'interface_id': u'1030',
                                 'interfaces': [{'nodes': [{'address': u'130.130.130.130',
                                                            'network_value': u'130.130.130.0/24',
                                                            'nodeid': 1}]}],
                                 'type': 'tunnel_interface',
                                 'zone_ref': u'myzone'},
                                {'interface_id': u'52',
                                 'interfaces': [{'nodes': [{'address': u'53.53.53.53',
                                                            'network_value': u'53.53.53.0/24',
                                                            'nodeid': 1}],
                                                 'vlan_id': u'53'},
                                                {'comment': u'comment for interface 52',
                                                 'nodes': [{'address': u'52.52.52.52',
                                                            'network_value': u'52.52.52.0/24',
                                                            'nodeid': 1}],
                                                 'vlan_id': u'52'}]},
                                {'comment': u'comment for interface 49',
                                 'interface_id': u'51',
                                 'interfaces': [{'nodes': [{'address': u'51.51.51.1',
                                                            'network_value': u'51.51.51.0/24',
                                                            'nodeid': 1}]}]},
                                {'interface_id': u'1005',
                                 'interfaces': [{'nodes': [{'address': u'14.14.14.14',
                                                            'network_value': u'14.14.14.0/24',
                                                            'nodeid': 1}]}],
                                 'type': 'tunnel_interface'}],
                 'name': u'myfw2',
                 'primary_mgt': u'0',
                 'snmp': {'snmp_agent': u'testsnmp', 'snmp_interface': [u'3', u'2.8']}}
    
    #print(yaml.safe_dump(yaml_cluster(engine), default_flow_style=False, encoding=('utf-8')))

    ################################################################################
    
    inline_on_ips = {
        'interface_id': '20',
        'second_interface_id': '20',
        'interface': 'inline_ips_interface',
        'logical_interface_ref': 'interfaceref',
        'inspect_unspecified_vlans': True,
        'failure_mode': 'bypass',
        'interfaces': [{'logical_interface_ref': 'logical',
                        'vlan_id': 15,
                        'second_vlan_id': 17,
                        'zone_ref': 'vlan15 side a',
                        'second_zone_ref': 'vlan15 side b',
                        'comment': 'vlan15_comment'},
                        {'logical_interface_ref': 'logical2',
                         'vlan_id': 16}],
        'zone_ref': 'foozone',
        'second_zone_ref': 'foozone',
        'comment': 'mycomment'}
    

    engine = Engine('myfw')
    #TODO:
    # Remove getattr proxy from collections
    # Test InlineInterfaces with VLANs and delete
    # Tunnel interface routes are not removed after update and create when network changes - to_delete and invalid are not set when main interface is changed

    
    session.logout()
    sys.exit(1)
    
    
    #engine = Engine('newcluster')
    #itf = engine.interface.get(24)
    #pprint(itf.data.data)
    # External GW match is not exact: TODO:  BUG
    # GET /6.4/elements?filter=extgw4&filter_context=external_gateway&exact_match=True&case_sensitive=True
    # Returns: {"result":[{"href":"https://172.18.1.151:8082/6.4/elements/external_gateway/69","name":"extgw3","type":"external_gateway"}]}
    
    session.logout()
    sys.exit(1)
    
    # BUG: Cannot update NAT translation ports
    # Should be able to remove translation ports??
    
    #session.logout()
    #sys.exit(1)
    #rule = policy.search_rule('dstandsrcnat')
    #if rule:
    #    pprint(rule[0].data)
    #    print(rule[0].static_dst_nat.translated_ports)
        
    # Bug when destination cannot be resolved in NAT dest
    '''
    policy.fw_ipv4_nat_rules.create(
            name='dstandsrcnat',
            sources='any',
            destinations=[Host('kali')],
            services='any',
            dynamic_src_nat='5.5.5.10',
            static_dst_nat='3.3.3.3',
            static_dst_nat_ports=(22, 2222))
    '''
    
    
    #yaml_cluster(engine)
    #print(yaml.safe_dump(yaml_cluster(engine), default_flow_style=False, encoding=('utf-8')))                
    
   

    # Management to single IP on VLAN interface with multiple IPs    
    
    session.logout()
    sys.exit(1)

    import inspect
    def generic_type_dict(clazz):
        """
        Derive a type dict based on any element
        
        :param Element clazz: a class of type element
        :rtype: dict
        """
        types = dict()
        attr = inspect.getargspec(clazz.create).args[1:]
        types[clazz.typeof] = {'attr': attr}
        return types
    
    pprint(generic_type_dict(AutonomousSystem))
    
    engine = Engine('myfw')
    
    #TODO: Version 6.3.4 / 6.4
    
    # Filter for reports
    # ActiveAlerts
    #tls_profile
    #tls_inspection_policy
    #tls_cryptography_suite_set
    #for x in Search.objects.entry_point('tls_cryptography_suite_set'):
    #    pprint(x.data)
    
    
    class element(object):
        """
        Descriptor can be placed on a method that returns href's
        that should be resolved into Elements.
        """
        def __init__(self, fget):
            self.fget = fget
     
        def __get__(self, instance, owner=None):  # @UnusedVariable
            if instance is None:
                return self
            href = self.fget(instance)
            if isinstance(href, list):
                return [Element.from_href(ref) for ref in href]
            return Element.from_href(href)


    #IndexedIterable()
    #### 
    # Type Hint for eclipse
    # assert isinstance(policy.fw_ipv4_access_rules, IPv4Rule)
    
    
    # Interface should mask __getitem__ or just document that indexing is not supported?
    #   
    # decorator for deleting cache that handles exception raising in function
    # Rule needs an update method - clear _cache before calling
    # Need to rename 'addresses' and 'add_arp' in interfaces to avoid proxying these
    # override update on interface, remove save?
    # Consider this for property documentation:
    #     :getter: Returns this direction's name
    #     :setter: Sets this direction's name
    #     :type: string

  

    #session.logout()
    
    
    import smc.elements.network as network
    import smc.elements.group as group
    
    
    def network_elements():   
        types = dict(
            host=dict(type=network.Host),
            network=dict(type=network.Network),
            address_range=dict(type=network.AddressRange),
            router=dict(type=network.Router),
            ip_list=dict(type=network.IPList),
            group=dict(type=group.Group),
            interface_zone=dict(type=network.Zone),
            domain_name=dict(type=network.DomainName))
        
        for t in types.keys():
            clazz = types.get(t)['type']
            types[t]['attr'] = inspect.getargspec(clazz.create).args[1:]
        
        return types
    
    def ro_network_elements():
        types = dict(
            alias=dict(type=network.Alias),
            country=dict(type=network.Country),
            expression=dict(type=network.Expression),
            engine=dict(type=Engine))
    
        for t in types.keys():
            clazz = types.get(t)['type']
            types[t]['attr'] = inspect.getargspec(clazz.__init__).args[1:]
        
        return types
    
    ELEMENT_TYPES = network_elements()
    ELEMENT_TYPES.update(ro_network_elements())

    
    #g = Group('group_referencing_existing_elements')
    #print([x.href for x in g.obtain_members()])
    #pprint(element_dict_from_obj(g, ELEMENT_TYPES, expand=['group']))
    
    # All other elements use name/comments to search
    SEARCH_HINTS = dict(
        network='ipv4_network',
        address_range='ip_range',
        host='address',
        router='address'
    )
    
    def is_element_valid(element, type_dict, check_required=True):
        """
        Are all provided arguments valid for this element type.
        Name and comment are valid for all.
        
        :param dict element: dict of element
        :param bool check_required: check required validates that at least
            one of the required arguments from the elements `create` constructor
            is provided. This is set to True when called from the network_element
            or service_element modules. This can be False when called from the
            firewall_rule module which allows an element to be fetched only.
        :return: None
        """
        for key, values in element.items():
            if not key in type_dict:
                return 'Unsupported element type: {} provided'.format(key)
    
            valid_values = type_dict.get(key).get('attr', [])

            # Verify that all attributes are supported for this element type
            provided_values = values.keys() if isinstance(values, dict) else []
            if provided_values:
                # Name is always required
                if 'name' not in provided_values:
                    return 'Entry: {}, missing required name field'.format(key)
            
                for value in provided_values:
                    if value not in valid_values:
                        return 'Entry type: {} with name {} has an invalid field: {}. '\
                            'Valid values: {} '.format(key, values['name'], value, valid_values)
                
                if check_required:
                    required_arg = [arg for arg in valid_values if arg not in ('name', 'comment')]
                    if required_arg: #Something other than name and comment fields
                        if not any(arg for arg in required_arg if arg in provided_values):
                            return 'Missing a required argument for {} entry: {}, Valid values: {}'\
                                .format(key, values['name'], valid_values)
                
                if 'group' in element and values.get('members', []):
                    for element in values['members']:
                        if not isinstance(element, dict):
                            return 'Group {} has a member: {} with an invalid format. Members must be '\
                                'of type dict.'.format(values['name'], element)
                        invalid = is_element_valid(element, type_dict, check_required=False)
                        if invalid:
                            return invalid
            else:
                return 'Entry type: {} has no values. Valid values: {} '\
                    .format(key, valid_values)
        
    
    elements = [
                {
                    "address": "1.1.1.1", 
                    "host": "foobar4562"
                }, 
                {
                    "comment": "foo",
                    "ipv4_network": "1.1.0.0/24",
                    "network": "foonetwork1.2.3"
                },
                {
                    "network": "any"
                },
                {
                    "address_range": "myrange3", 
                    "ip_range": "3.3.3.1-3.3.3.5"
                }, 
                {
                        "address": "172.18.1.254", 
                        "ipv6_address": "2003:dead:beef:4dad:23:46:bb:101", 
                        "router": "myrouter2", 
                        "secondary": [
                            "172.18.1.253"
                        ]
                },
                {
                    "alias": "$ EXTERNAL_NET",
                }, 
                {
                    "domain_name": "dogpile.com",
                    "comment": "bar"
                }, 
                {
                    "interface_zone": "external_zone123"
                },
                {
                    "interface_zone": "new123zone",
                    "comment": "dingo"
                },
                {
                    "ip_list": "mylist",
                    "iplist": ['45.45.45.45']
                }, 
                {
                    "group": "doodoo",
                    "members": [
                        {'host': {'name':'blah'}
                        }]
                }, 
                {
                    "country": [
                        "Armenia", 
                        "United States", 
                        "China"
                    ]
                }, 
                {
                    "engine": [
                        "fw2", 
                        "myfirewall"
                    ]
                }
            ]            
    
    
    NETWORK_ELEMENTS = ELEMENT_TYPES.keys()
    
    
    def extract_element(element, type_dict):
        """
        Extract a dict like yml entry. Split this into a dict in
        the correct format if the element type exists.
        """
        key = [key for key in set(element) if key in type_dict]
        if key and len(key) == 1:
            typeof = key.pop()
            element['name'] = element.pop(typeof)
            return typeof, {typeof: element}

    def is_field_any(field):
        """
        Is the source/destination or service field using an ANY
        value.
        
        :rtype: bool
        """
        if 'network' in field and field['network']['name'].upper() == 'ANY':
            return True
        return False
    
    def update_or_create(element, type_dict, hint=None, check_mode=False):
        """
        Create or get the element specified. The strategy is to look at the
        element type and check the default arguments. Some elements require
        only name and comment to create. Others require specific arguments.
        If only name and comment is provided and the constructor requires
        additional args, try to fetch the element, otherwise call
        get_or_create. If the constructor only requires name and comment,
        these will also call get_or_create.
        
        :param dict element: element dict, key is typeof element and values
        :param dict type_dict: type dict mappings to get class mapping
        :param str hint: element attribute to use when finding the element
        :raises CreateElementFailed: may fail due to duplicate name or other
        :raises ElementNotFound: if fetch and element doesn't exist
        :return: The result as type Element
        """
        for typeof, values in element.items():
            type_dict = type_dict.get(typeof)
            
            filter_key = {hint: values.get(hint)} if hint in values else None
            raise_exc = False if check_mode else True
            
            if check_mode:
                result = type_dict['type'].get(values.get('name'), raise_exc)
                if result is None:
                    return dict(
                        name=values.get('name'),
                        type=typeof,
                        msg='Specified element does not exist')
            else:
                attr_names = type_dict.get('attr', []) # Constructor args
                provided_args = set(values)
                
                # Guard against calling update_or_create for elements that
                # may not be found and do not have valid `create` constructor
                # arguments
                if set(attr_names) == set(['name', 'comment']) or \
                    any(arg for arg in provided_args if arg not in ('name',)):
                    
                    result = type_dict['type'].update_or_create(filter_key=filter_key, **values)
                else:
                    print("Only perform GET!")
                    result = type_dict['type'].get(values.get('name'))

                return result
            
            
    def get_or_create_element(element, type_dict, hint=None, check_mode=False):
        """
        Create or get the element specified. The strategy is to look at the
        element type and check the default arguments. Some elements require
        only name and comment to create. Others require specific arguments.
        If only name and comment is provided and the constructor requires
        additional args, try to fetch the element, otherwise call
        get_or_create. If the constructor only requires name and comment,
        these will also call get_or_create.
        
        :param dict element: element dict, key is typeof element and values
        :param dict type_dict: type dict mappings to get class mapping
        :param str hint: element attribute to use when finding the element
        :raises CreateElementFailed: may fail due to duplicate name or other
        :raises ElementNotFound: if fetch and element doesn't exist
        :return: The result as type Element
        """
        for typeof, values in element.items():
            type_dict = type_dict.get(typeof)
    
        # An optional filter key specifies a valid attribute of
        # the element that is used to refine the search so the
        # match is done on that exact attribute. This is generally
        # useful for networks and address ranges due to how the SMC
        # interprets / or - when searching attributes. This changes
        # the query to use the attribute for the top level search to
        # get matches, then gets the elements attributes for the exact
        # match. Without filter_key, only the name value is searched.
        filter_key = {hint: values.get(hint)} if hint in values else None
        
        if check_mode:
            #print(type_dict['type'].get(values.get('name')))
            #result = type_dict['type'].get(values.get('name'), raise_exc=False)
            print("Filter key: %s" % filter_key)
            if filter_key:
                print("Via filter key: %s" % filter_key)
                result = type_dict['type'].objects.filter(**filter_key).first()
            else:
                print("No filter")
                result = type_dict['type'].objects.filter(values.get('name')).first()
            print("Result: %s" % result)
            if result is None:
                return dict(
                    name=values.get('name'),
                    type=typeof,
                    msg='Specified element does not exist')
        else:
            result = type_dict['type'].get_or_create(filter_key=filter_key, **values)
            return result
    
    print(get_or_create_element({'autonomous_system': {'name': 'fooas', 'as_number': '100'}},
                                 {'autonomous_system': {'type': AutonomousSystem}}, hint='as_number', check_mode=True))
    
    
    #import timeit
    #print(timeit.repeat("test()",
    #                    setup="from __main__ import test", number=1000000,
    #                    repeat=3))

    #tls = TLSServerCredential.create(name='tlstest', common_name="CN=myserver.lepages.local")
    #tls = TLSServerCredential('LePagesCA')
    #pprint(tls.data)
    
    
    print(vars(session))
    #c = copy.copy(session)
    #print("Copy of...")
    #print(vars(c))
    print("Switch domain to nsx.....")
    session.switch_domain('nsx')
    print(vars(session))
    print(session.domain)
    
    #print("copied instance after switching domains: %s" % vars(c))
    result = SMCRequest(params={'filter_context': 'single_fw',
                                'exact_match': False,
                                'domain': 'nsx'}).read()
    print(result)
    for x in session.entry_points.all():
        if 'tls' in x:
            print(x)

    engine = Engine('bar')
    pprint(engine.data)
    
    #ClientProtectionCA.create('foo')
    print(engine.server_credential)
        
    #    print(x.certificate_export())

        
        
        
    
    # Daily
    {'day_period': 'daily',
     'minute_period': 'hourly', # every hour
     'minute_period': 'each_half', # each half hour
     'minute_period': 'each_quarter'} # every 15 minutes
    
    # Weekly - I cant figure out the day mask
    {'day_period': 'weekly',
     'minute_period': 'one_time',
     'day_mask': 124 # Mon - Friday
     }
    
    # Monthly
    {'day_period': 'monthly',
     'minute_period': 'one_time'}
    
    # Yearly
    {'day_period': 'yearly',
     'minute_period': 'one_time'}
    
    a = {u'activated': True,
         u'activation_date': '2017-10-04T09:33:09.890000-05:00',
         u'comment': u'test',
         u'day_mask': 0,
         u'day_period': u'one_time',
         u'final_action': u'ALERT_FAILURE',
         u'minute_period': u'one_time',
         u'name': u'test7'}
    
    #b = prepared_request(href='https://172.18.1.151:8082/6.3/elements/refresh_policy_task/42/task_schedule',
    #                     json=a).create()
    #print(b)
    
    '''
    export_log_task
    archive_log_task
    remote_upgrade_task
    '''
    #client_gateway
    #validate_policy_task
    #refresh_policy_task
    
    #print(get_options_for_link('https://172.18.1.151:8082/6.3/elements/fw_alert'))
    
         
    import pexpect  # @UnresolvedImport
    import tempfile
   
    def ssh(host, cmd, user, password, timeout=15, bg_run=False):                                                                                                 
        """SSH'es to a host using the supplied credentials and executes a command.                                                                                                 
        Throws an exception if the command doesn't return 0.                                                                                                                       
        bgrun: run command in the background"""                                                                                                                                    
    
        fname = tempfile.mktemp()                                                                                                                                                  
        fout = open(fname, 'w')                                                                                                                                                    
    
        options = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'                                                                         
        if bg_run:                                                                                                                                                         
            options += ' -f'                                                                                                                                                       
        ssh_cmd = 'ssh %s@%s %s "%s"' % (user, host, options, cmd)
        print("SSH CMD: %s" % ssh_cmd)                                                                                                               
        child = pexpect.spawn(ssh_cmd, timeout=timeout)
        
        #child.expect(['[sudo] password for nsxadmin: '])
        #child.sendline(password)
        child.expect(['Password: '])                                                                                                                                                                                                                                                                                               
        child.sendline(password)
        if 'sudo' in ssh_cmd:
            child.expect(['sudo'])
            child.sendline(password)                                                                                                                                          
        #child.logfile = fout
        child.logfile = sys.stdout.buffer                                                                                                                                                      
        child.expect(pexpect.EOF)                                                                                                                                                  
        child.close()                                                                                                                                                              
        fout.close()                                                                                                                                                               
    
        fin = open(fname, 'r')                                                                                                                                                     
        stdout = fin.read()
        fin.close()                                                                                                                                                                
    
        if 0 != child.exitstatus:                                                                                                                                                  
            raise Exception(stdout)                                                                                                                                                
    
        return stdout
    
    
    cmd = 'sudo -u root -S msvc -r dpa'
    #print(ssh('172.18.1.111', cmd=cmd, user='nsxadmin', password='password'))
    

    
    from smc.administration.system import System
    for x in Search.objects.entry_point('tls_server_credentials').all():
        if x.name == 'lepages':
            pprint(x.data)

   
            
    
    
    class ProbingProfile(Element):
        typeof = 'probing_profile'
        def __init__(self, name, **meta):
            super(ProbingProfile, self).__init__(name, **meta)
    
    class ThirdPartyMonitoring(object):
        def __init__(self, log_server=None, probing_profile=None,
                     netflow=False, snmp_trap=False):

            if not log_server:
                log_server = LogServer.objects.first()

            self.monitoring_log_server_ref = element_resolver(log_server)

            if not probing_profile:
                probing_profile = ProbingProfile.objects.filter('Ping').first()

            self.probing_profile_ref = element_resolver(probing_profile)

            self.netflow = netflow
            self.snmp_trap = snmp_trap

        def __call__(self):
            return vars(self)



    #host.third_party_monitoring = ThirdPartyMonitoring()
    #print(vars(host))
    #host.update()

    #t = ThirdPartyMonitoring()
    #host.third_party_monitoring = t

    #print("Finished polling, result is: %s" % poller.result())
    vss_def = {"isc_ovf_appliance_model": 'virtual',
               "isc_ovf_appliance_version": '',
               "isc_ip_address": '1.1.1.1',
               "isc_vss_id": 'foo',
               "isc_virtual_connector_name": 'smc-python'}

    vss_node_def = {
            'management_ip': '4.4.4.6',
            'management_netmask': '24',
            'isc_hypervisor': 'default',
            'management_gateway': '2.2.2.1',
            'contact_ip': None}
    '''
    rbvpn_tunnel_side
    rbvpn_tunnel_monitoring_group
    rbvpn_tunnel
    '''
  
    
    
            
    '''
    by_action = {
        "format": {
            "type": "texts",
            "field_ids": "name"
        },
        "query": {
            "type":"stored",
            "filter": {
                "type": "in",
                "left": {
                    "type": "field",
                    "name": LogField.ACTION},
                "right":[
                    {"type": "constant", "value":Actions.DISCARD}]}
        },
        "fetch":{"quantity":100}
    }
    
    by_protocol = {
        "format": {
            "type": "texts",
            "field_format": "name"
        },
        "query": {
            "type":"stored",
            "filter": {
                "type": "in",
                "left": {
                    "type": "field",
                    "name": "Protocol"
                },
                "right":[{
                    "type": "number",
                    "value":6}]
            }
        },
        "fetch":{"quantity":100}
    }
    
    by_service = {
        "format": {
            "type": "texts",
            "field_format": "name"
        },
        "query": {
            "type":"stored",
            "filter": {
                "type": "in",
                "left": {
                    "type": "field",
                    "name": "Service"},
                "right":[
                    {"type": "service",
                     "value": "TCP/80"}]
            }
        },
        "fetch":{"quantity":100}
    }
    
    by_sender = {
        "format": {
            "type": "texts",
            "field_format": "name"
        },
        "query": {
            "type":"stored",
            "filter": {
                "type": "in",
                "left": {
                    "type": "id",
                    "name": LogField.SRC},
                "right":[
                    {"type": "ip",
                     "value": "1.1.1.1"}]
            }
        },
        "fetch":{"quantity":100}
    }

    ip_and_service = {
        "format": {
            "type": "texts",
            "field_format": "name"
        },
        "query": {
            "type":"stored",
            "start_ms": 0,
            "end_ms": 0,
            "filter": {
                "type": "and",
                "values": [
                    {"type": "in",
                     "left": {
                         "type": "field",
                         "name": "Service"},
                     "right":[
                         {"type": "service",
                          "value": "TCP/443"}]
                    },
                    {"type": "in",
                     "left": {
                         "type": "field",
                         "id": LogField.SRC},
                     "right":[
                         {"type": "ip",
                          "value": "192.168.4.84"}]
                    },       
                    ]
            }
        },
        "fetch":{"quantity":100}
    }
    
    
    cs_like_filter = {
        "format": {
            "type": "texts",
            "field_format": "name"
        },
        "query": {
            "type":"stored",
            "filter": {
                "type": "ci_like",
                "left": {
                    "type": "field",
                    "id": LogField.INFOMSG},
                "right": {
                    "type": "string", 
                    "value":"Connection was reset by client" }
                }
        },
        "fetch":{"quantity":100}
    }
    
    bl2 = {
        'fetch': {},
        'format': {
            "type": "texts",
            "field_format": "name",
            "resolving": {
                "senders": True}
        },
        'query': {
            'definition': 'BLACKLIST', 
            'target': 'sg_vm'}
    }
    
    blacklist = {
        'fetch': {},
        'format': {
            'type': 'combined',
            'formats': {
                "fields": {
                    "type": "detailed",
                    "field_format": "name"
                },
                "bldata": {
                    "type": "texts",
                    "field_format": "name",
                    "resolving": {"time_show_zone": True,
                                  "timezone": "CST"
                    }
                },
                "blentry": {
                    "type": "texts",
                    "field_format": "pretty",
                    "field_ids": [LogField.BLACKLISTENTRYID]
                }
            }
        },
        'query': {
            'definition': 'BLACKLIST', 
            'target': 'sg_vm'}
    }
    '''
    '''
    ids = resolve_field_ids(list(range(1000)))
    for x in ids:
        pprint(x)
    for x in reversed(ids):
        print('{}={} #: {}'.format(
            x.get('name').upper(),
            x.get('id'),
            x.get('comment')))

    sys.exit(1)
    '''
    
    
    
    #import timeit
    #print(timeit.repeat("{link['rel']:link['href'] for link in links}",
    #                    setup="from __main__ import links", number=1000000,
    #                    repeat=3))
    
    #import timeit
    # print(timeit.timeit("ElementFactory('http://172.18.1.150:8082/6.1/elements/host/978')",
    # setup="from __main__ import ElementFactory", number=1000000))

    #print(timeit.timeit("find_link_by_name('self', [])", setup="from smc.base.util import find_link_by_name"))


    print(time.time() - start_time)
    session.logout()
