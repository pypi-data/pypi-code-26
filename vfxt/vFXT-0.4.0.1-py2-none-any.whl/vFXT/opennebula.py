#!/usr/bin/env python2.7
# Copyright (c) 2015-2018 Avere Systems, Inc.  All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
'''
Avere OpenNebula vFXT automation
'''
import logging
import time
import math
import threading
import Queue
import argparse
import socket
import urlparse
import urllib
import re
import getpass
import ssl
import xmlrpclib
try:
    import defusedxml.xmlrpc
    defusedxml.xmlrpc.monkey_patch()
except ImportError: pass

import vFXT
from vFXT.service import vFXTServiceTimeout, vFXTConfigurationException, vFXTServiceFailure, vFXTNodeExistsException, vFXTCreateFailure
from vFXT import ServiceInstance, ServiceBase, Cluster
import oca

log = logging.getLogger(__name__)

class Service(ServiceBase):
    '''OpenNebula vFXT Service backend
    '''
    ON_STATUS="RUNNING"
    OFF_STATUS="LCM_INIT"
    NTP_SERVERS=['ntp0.lab.avere.net', 'ntp1.lab.avere.net', 'ntp2.lab.avere.net']
    DNS_SERVERS=[]
    ENDPOINT_HOST='one.lab.avere.net:2633'
    ENDPOINT_FORMAT='http://{}/RPC2'

    def __init__(self, network, username, password, **options):
        '''Constructor

            Arguments:
                network (str): OpenNebula Network name
                username (str): OpenNebula user name
                password (str): OpenNebula user password
                proxy (str, optional): proxy URI for proxying API calls
                endpoint (str, optional): OpenNebula RPC host, defaults to ENDPOINT_HOST
                endpoint_format (str, optional): OpenNebula RPC URL template, defaults to ENDPOINT_FORMAT

                no_connection_test (bool, optional): skip connection test
        '''
        self.network    = network
        self.user       = username
        self.passwd     = password
        self.proxy      = options.get('proxy') or None
        self.local      = threading.local()
        self.endpoint   = options.get('endpoint') or self.ENDPOINT_HOST
        self.endpoint_fmt = options.get('endpoint_format') or self.ENDPOINT_FORMAT

        if options.get('no_connection_test', None):
            return

        self.connection_test()

    def connection_test(self):
        '''Connection test

            Raises: vFXTConfigurationException
        '''
        try:
            conn = self.connection()
            log.debug("Using OpenNebula version {}".format(conn.version()))
        except Exception as e:
            raise vFXTConfigurationException("Unable to authentication to OpenNebula service: {}".format(e))

    def connection(self):
        '''Connection factory, returns a new connection or thread local copy
        '''
        if not hasattr(self.local, 'connection'):
            log.debug("Creating new connection object")
            cred = '{}:{}'.format(self.user, self.passwd)
            url  = self.endpoint_fmt.format(self.endpoint)
            proxy = None if not self.proxy else urlparse.urlparse(self.proxy).netloc or self.proxy
            self.local.connection = oca.Client(cred, url, proxy=proxy)
        # XXX timeout?
        return self.local.connection

    @classmethod
    def get_instance_data(cls, source_address=None):
        '''Detect the instance data
            Arguments:
                source_address (str, optional): source address for data request

            This only works when running on a OpenNebula instance.
        '''
        raise NotImplementedError()

    @classmethod
    def on_instance_init(cls, source_address=None, no_connection_test=False):
        '''Init an OpenNebula service object from on instance metadata

            Arguments:
                source_address (str, optional): source address for data request
                no_connection_test (bool, optional): skip connection tests, defaults to False
            This is only meant to be called on instance.  Otherwise will
            raise a vFXTConfigurationException exception.
        '''
        raise NotImplementedError()

    def find_instances(self, filterdict=None):
        '''Returns all or filtered list of instances

            Arguments:
                filterdct (dict, optional): search query

            Examples:
                {'range_start': first_id, 'range_end': last_id, 'vm_state': 3, 'filter': -2}

                where vm_state is:
                    -2 Any state, including DONE
                    -1 Any state, except DONE (Defualt)
                    0 INIT
                    1 PENDING
                    2 HOLD
                    3 ACTIVE
                    4 STOPPED
                    5 SUSPENDED
                    6 DONE
                    7 FAILED

                where filter is
                    -3: Connected user's resources
                    -2: All resources
                    -1: Connected user's and his group's resources
                     > = 0: UID User's Resources
        '''
        conn = self.connection()
        pool = oca.VirtualMachinePool(conn)

        filterdict = filterdict or {}
        filterdict['vm_state'] = filterdict.get('vm_state') or -1
        filterdict['filter'] = filterdict.get('filter') or -2
        pool.info(**(filterdict or {}))
        return pool

    def get_instances(self, instance_ids):
        '''Returns a list of instances with the given instance ID list

            Arguments:
                instance_ids ([int]): list of instance id values

            Returns:
                [objs]: list of backend instance objects
        '''
        try:
            test = int(instance_ids[0]) # pylint: disable=unused-variable
            return self.find_instances({'range_start': min(instance_ids), 'range_end': max(instance_ids)})
        except ValueError:
            # NOTE: no support for fetching instance by name
            return [_ for _ in self.find_instances() if _.name in instance_ids]

    def get_instance(self, instance_id):
        '''Get a specific instance by instance ID

            Arguments:
                instance_id (int)

            Returns:
                obj or None
        '''
        try:
            instance_id = int(instance_id)
            r = self.find_instances({'range_start': int(instance_id), 'range_end': int(instance_id)})
            if r:
                return r[0]
        except ValueError:
            # NOTE: no support for fetching instance by name
            instance = [_ for _ in self.find_instances() if _.name == instance_id]
            if instance:
                return instance[0]
        return None

    def wait_for_status(self, instance, status, retries=120): # maybe refactor into base class?
        '''Pool on a given instance for status

            Arguments:
                instance (obj): backend instance object
                status (str): status string to watch for
                retries (int=120): number of retries

            Raises: vFXTServiceTimeout
        '''
        s = '...' # in case our instance is not yet alive
        while status != s:
            if retries % 10 ==0: # rate limit
                log.debug("Waiting for status: {} != {} for {}".format(s, status, self.name(instance)))
            time.sleep(self.POLLTIME)
            try:
                instance = self.refresh(instance)
                s = self.status(instance)
                if 'FAILURE' in s:
                    raise vFXTServiceFailure("Failed to wait for {} on {}: {}".format(status, self.name(instance), s))
            except Exception as e:
                log.debug('Ignored: {}'.format(e))
                time.sleep(2)
            retries -= 1
            if retries == 0:
                err = self._get_instance_xml_data(instance).get('error', None)
                if err:
                    raise vFXTServiceTimeout("Failed waiting for {} on {}: {}".format(status, self.name(instance), err))
                else:
                    raise vFXTServiceTimeout("Failed waiting for {} on {}".format(status, self.name(instance)))

    def wait_for_service_checks(self, instance, retries=600):
        pass

    def stop(self, instance, wait=600):
        '''Stop an instance

            Arguments:
                instance: backend instance
                wait (int): wait time
        '''
        if not self.can_stop(instance):
            raise vFXTConfigurationException("Node configuration prevents them from being stopped")
        log.info("Stopping instance {}".format(self.name(instance)))
        instance.poweroff()
        self.wait_for_status(instance, self.OFF_STATUS, retries=wait)

    def start(self, instance, wait=600):
        '''Start an instance

            Arguments:
                instance: backend instance
                wait (int): wait time
        '''
        log.info("Starting instance {}".format(self.name(instance)))
        instance.resume()
        self.wait_for_status(instance, self.ON_STATUS, retries=wait)

    def restart(self, instance):
        '''Restart an instance

            Arguments:
                instance: backend instance
        '''
        if not self.can_stop(instance):
            raise vFXTConfigurationException("Node configuration prevents them from being restarted")
        log.info("Restarting instance {}".format(self.name(instance)))
        # XXX revisit... how to watch the slow state transitions of OpenNebula
        self.stop(instance)
        self.start(instance)

    def destroy(self, instance, retries=ServiceBase.WAIT_FOR_DESTROY):
        '''Destroy an instance

            Arguments:
                instance: backend instance
                retries (int, optional): number of retries
        '''
        log.info("Destroying instance {}".format(self.name(instance)))
        instance.shutdown()
        self.wait_for_status(instance, self.OFF_STATUS, retries=retries)
        instance.delete()

    def is_on(self, instance):
        '''Return True if the instance is currently on

            Arguments:
                instance: backend instance
        '''
        return self.status(instance) != self.OFF_STATUS

    def is_off(self, instance):
        '''Return True if the instance is currently off

            Arguments:
                instance: backend instance
        '''
        return self.status(instance) == self.OFF_STATUS

    def name(self, instance):
        '''Returns the instance name (may be different from instance id)

            Arguments:
                instance: backend instance
        '''
        return instance.name

    def instance_id(self, instance):
        '''Returns the instance id (may be different from instance name)

            Arguments:
                instance: backend instance
        '''
        return instance.id

    def ip(self, instance):
        '''Return the primary IP address of the instance

            Arguments:
                instance: backend instance
        '''
        data = self._get_instance_xml_data(instance)
        return data['ip'] if 'ip' in data else None

    def fqdn(self, instance):
        '''Provide the fully qualified domain name of the instance

            Arguments:
                instance: backend instance
        '''
        data = self._get_instance_xml_data(instance)
        #return data['hostname']
        return data['name']

    def status(self, instance):
        '''Return the instance status

            Arguments:
                instance: backend instance
        '''
        state = lcm_state = 'UNKNOWN'
        try:
            lcm_state = instance.str_lcm_state
            state     = instance.str_state
        except Exception as e:
            log.debug("Error getting status: {}".format(e))
        log.debug('state: {}, lcm_state: {}'.format(state, lcm_state))
        # XXX revisit, str_state and str_lcm_state are ambigious, and
        # poweroff() hits a bug in oca
        return lcm_state

    def refresh(self, instance):
        '''Refresh the instance from the OpenNebula backend

            Arguments:
                instance: backend instance
        '''
        instance.info()
        return instance

    def can_stop(self, instance): # pylint: disable=unused-argument
        ''' Some instance configurations cannot be stopped. Check if this is one.

            Arguments:
                instance: backend instance
        '''
        return True

    def create_instance(self, machine_type, name, **options):
        '''Create and return an OpenNebula instance

            Arguments:
                machine_type (str): an OpenNebula template name
                name (str): name of the instance
                wait_for_success (int, optional): wait time for the instance to report success (default WAIT_FOR_SUCCESS)
                extra_template ({}, optional): extra key, value items to send in the extra template
                context ({}, optional): extra key, value items to send in the extra template within the context block

            Raises: vFXTConfigurationException, vFXTServiceFailure

            Service failures here are uncaught exceptions and should be handled
            by the caller.
        '''
        if not self.valid_instancename(name):
            raise vFXTConfigurationException("{} is not a valid instance name".format(name))
        if self.get_instance(name):
            raise vFXTNodeExistsException("{} exists".format(name))

        # our machine type is a template in OpenNebula
        templates = [_ for _ in self._list_templates() if _.name == machine_type]
        if not templates:
            raise vFXTConfigurationException("{} is not a valid template name".format(machine_type))
        template = templates[0]

        # construct the extra template (as xml or ini format)
        template_options = options.get('extra_template', {})
        extra_template = ',\n'.join(['{} = "{}"'.format(k.upper().replace('-','_'),v) for k,v in template_options.items()]) + '\n'
        if 'context' in options:
            context = options.get('context')
            context['NETWORK'] = 'YES'
            context = ',\n'.join(['{} = "{}"'.format(k.upper().replace('-','_'),v) for k,v in context.items()]) + '\n'
            extra_template += '\nCONTEXT = [ \n{}\n]'.format(context)

        try:
            log.debug("Instantiating template {}:{} as {} with template {}".format(template.name, template.id, name, extra_template))
            instance_id = template.instantiate(name, extra_template=extra_template)
            log.debug("created instance {}".format(instance_id))

            wait_for_success = options.get('wait_for_success') or self.WAIT_FOR_SUCCESS
            retries = self.CLOUD_API_RETRIES
            while retries > 0:
                instance = self.get_instance(instance_id)
                if instance:
                    self.wait_for_status(instance, self.ON_STATUS, retries=wait_for_success)
                    return instance
            raise vFXTServiceFailure("Unable to locate the created instance {}".format(name))
        except Exception as e:
            log.exception(e)
            raise vFXTServiceFailure("Create instance failed: {}".format(e))

    def create_node(self, node_name, cfg, node_opts, instance_options):
        '''Create a cluster node

            This is a frontend for create_instance that handles vFXT node specifics

            Arguments:
                node_name (str): name of the node
                cfg (str): configuration string to pass to the node
                node_opts (dict): node creation options
                instance_options (dict): options passed to create_instance

                node_opts include:
                    machine_type
        '''
        context = instance_options.pop('context', {})
        context['CLUSTER_CFG'] = ''.join(cfg.encode('base64').split()).strip()
        context['SET_HOSTNAME'] = node_name
        instance_options['context'] = context
        instance_options['extra_template'] = node_opts.get('extra_template', {})

        try:
            log.info("Creating node {}".format(node_name))
            n = self.create_instance(machine_type=node_opts['machine_type'], name=node_name, **instance_options)
            log.info("Created {} ({})".format(n.name, self.ip(n)))
            return n
        except (vFXTServiceFailure, vFXTConfigurationException) as e:
            log.debug(e)
            n = self.get_instance(node_name)
            if n:
                self.destroy(n)
            raise

    def create_cluster(self, cluster, **options):
        '''Create a vFXT cluster (calls create_node for each node)
            Typically called via vFXT.Cluster.create()

            Arguments:
                cluster (vFXT.cluster.Cluster): cluster object

                management_address (str): management address for the cluster
                address_range_start (str): Specify the first of a custom range of addresses to use
                address_range_end (str): cluster address range netmask
                address_range_netmask (str, optional): cluster address range netmask

                size (int, optional): size of cluster (node count)
                config_expiration (int, optional): expiration time for cluster join configuration
                wait_for_state (str, optional): red, yellow, green cluster state (defaults to yellow)
                skip_cleanup (bool, optional): do not clean up on failure
                extra_template ({}, optional): extra key, value items to send in the extra template
        '''
        machine_type    = cluster.machine_type
        cluster_size    = int(options.get('size') or 3)
        if machine_type not in [_.name for _ in self._list_templates()]:
            raise vFXTConfigurationException("{} is not a valid template".format(machine_type))

        allocated_addresses = []
        if not all([(options.get(_, None)) for _ in ['management_address', 'address_range_start', 'address_range_end']]):
            #raise vFXTConfigurationException("You must provide the management address and cluster range")
            log.info("Attempting to allocate mgmt/cluster IPs from the IT IP Management service")
            ipmgr = cluster.service._ip_mgmt_call()
            allocated_addresses = ipmgr.allocate(cluster.service.user, cluster_size+1, cluster.service.network)
            if not allocated_addresses or len(allocated_addresses) != cluster_size+1:
                raise vFXTConfigurationException("Unable to allocate enough IP addresses")
            options['management_address'] = allocated_addresses[0]
            options['address_range_start'] = allocated_addresses[1]
            options['address_range_end'] = allocated_addresses[-1]
            log.info("NOTE: If you manually destroy this cluster remember to release these addresses")
            log.info("ipcli.py release {}".format(' '.join(allocated_addresses)))
        else:
            # Validate
            r = vFXT.Cidr.expand_address_range(options.get('address_range_start'), options.get('address_range_end'))
            if len(r) < cluster_size:
                log.warn("Adding cluster address range without enough addresses for all nodes")

        cluster.mgmt_ip          = options.get('management_address')
        cluster.mgmt_netmask     = options.get('address_range_netmask') or self._get_network_data()['network_mask']
        cluster.cluster_ip_start = options.get('address_range_start')
        cluster.cluster_ip_end   = options.get('address_range_end')

        cfg     = cluster.cluster_config(expiration=options.get('config_expiration', None))
        log.debug("Generated cluster config: {}".format(cfg))

        extra_template = options.pop('extra_template', {})
        # Add extra options
        extra_template['MGMT_URL'] = 'https://{}/avere/fxt/'.format(cluster.mgmt_ip)

        try:
            # create the initial node
            name = '{}-{}'.format(cluster.name, 1)
            opts = {
                'machine_type': machine_type,
                'extra_template': extra_template.copy(),
            }
            n    = self.create_node(name, cfg, node_opts=opts, instance_options=options)
            cluster.nodes.append(ServiceInstance(service=self, instance=n))

            # need to make a license here since we cannot use the billing server on sims
            def gen_license(lic_id, lic_days=0, lic_nodes=20):
                ''' generate a license
                    lic_days (int, optional): # of days license is valid, 0 for forever
                    lic_nodes (int, optional): defaults to license up to 20 nodes
                '''
                import struct
                import uuid
                import hashlib
                DAY     =(24*60*60)         # seconds in a day
                exp     = 0 if not lic_days else (int(time.time()) + DAY - 1356998400)/DAY + lic_days
                node    = uuid.UUID(lic_id)
                feat    = 2395915001761103902 | (lic_nodes << 52) | (exp << 36)
                feat   ^= node.node
                feat    = struct.pack("q",feat)
                m       = hashlib.sha1()
                m.update(feat)
                m.update(str(node).lower().strip())
                return (feat+m.digest()[:8]).encode('base64')

            log.info("Waiting for remote API connectivity to {}".format(cluster.mgmt_ip))
            xmlrpc = cluster.xmlrpc(retries=60) #pylint: disable=unused-variable
            log.info("Granting temp license")
            cluster_id  = xmlrpc.cluster.listLicenses()['clusterUUID']
            license_key = gen_license(cluster_id)
            retries = cluster.service.XMLRPC_RETRIES
            while True:
                response = None
                try:
                    response = xmlrpc.cluster.addLicense(license_key)
                    if response == 'success':
                        break
                except Exception as e:
                    log.debug('Ignoring: {}'.format(e))
                    log.debug("Failed to license cluster: {}, retrying.".format(response))
                retries -= 1
                if retries == 0:
                    raise vFXTConfigurationException("Failed to license cluster: {}".format(response))

            if not options.get('skip_configuration'):
                cluster.first_node_configuration()

            # Create the rest of the nodes
            self.add_cluster_nodes(cluster, cluster_size - 1, **options)
        except vFXTNodeExistsException as e:
            log.error("Failed to create node: {}".format(e))
            if allocated_addresses:
                cluster.service._ip_mgmt_call().release(allocated_addresses)
            raise
        except Exception as e:
            log.exception("Failed to create node: {}".format(e))
            if not options.get('skip_cleanup', False):
                if allocated_addresses:
                    cluster.service._ip_mgmt_call().release(allocated_addresses)
                cluster.destroy()
            raise vFXTCreateFailure(e)

    def post_destroy_cluster(self, cluster):
        '''Post cluster destroy cleanup
        '''
        pass

    def _add_cluster_nodes_setup(self, cluster, count, **options):
        '''OpenNebula specific customization prior to adding nodes
        '''
        pass

    def add_cluster_nodes(self, cluster, count, **options):
        '''Add nodes to the cluster (delegates to create_node())

            Arguments:
                cluster (vFXT.cluster.Cluster): cluster object
                count (int): number of nodes to add
                skip_cleanup (bool, optional): do not clean up on failure
                **options: passed to create_node()

            Raises: exceptions from create_node()
        '''
        # Requires cluster be online
        # XXX assume our node name always ends in the node number
        max_node_num = max([int(i.name().split('-')[-1]) for i in cluster.nodes])

        machine_type = cluster.machine_type
        joincfg = cluster.cluster_config(joining=True, expiration=options.get('config_expiration', None))
        log.debug("Generated cluster join config: {}".format(joincfg))

        nodeq   = Queue.Queue()
        failq   = Queue.Queue()
        threads = []

        def cb(nodenum, inst_opts, nodeq, failq):
            '''callback
            '''
            opts = { 'machine_type': machine_type }
            try:
                name = '{}-{}'.format(cluster.name, nodenum)
                n    = self.create_node(name, joincfg, node_opts=opts, instance_options=inst_opts)
                nodeq.put(n)
            except Exception as e:
                failq.put("Failed to create node: {}".format(e))

        for node_num in xrange(max_node_num, max_node_num+count):
            next_node_num = node_num + 1
            inst_opts = options.copy()
            t = threading.Thread(target=cb, args=(next_node_num, inst_opts, nodeq, failq,))
            t.setDaemon(True)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        nodes = []
        while True:
            try:
                n = nodeq.get_nowait()
                nodes.append(ServiceInstance(service=self, instance=n))
            except Queue.Empty:
                break

        failed = []
        while True:
            try:
                failed.append(failq.get_nowait())
            except Queue.Empty:
                break
        if failed:
            if not options.get('skip_cleanup', False):
                for n in nodes:
                    n.destroy()
            raise Exception(failed)

        cluster.nodes.extend(nodes)

    def load_cluster_information(self, cluster, **options):
        '''Loads cluster information from the service and cluster itself
        '''
        xmlrpc = cluster.xmlrpc()

        # make sure mgmt_ip is set to the valid address (in case we used
        # a node address to get in)
        cluster.mgmt_ip = xmlrpc.cluster.get()['mgmtIP']['IP']

        node_ips = set([n['primaryClusterIP']['IP']
                        for name in xmlrpc.node.list()
                        for n in [xmlrpc.node.get(name)[name]]
                        if 'primaryClusterIP' in n])

        # lookup nodes that have one of our primary IP addresses.. for now we
        nodes = [_ for _ in self.find_instances() if self.ip(_) in node_ips]
        if nodes:
            cluster.nodes        = [ServiceInstance(self, instance=_) for _ in nodes]
            # XXX assume all instances have the same settings
            n                    = nodes[0]
            cluster.machine_type = [_ for _ in self._list_templates() if str(n.template.template_id) in [str(_.id), _.name]][0].name
            cluster.network      = self._get_instance_xml_data(n)['network']

    def shelve(self, instance):
        raise NotImplementedError()
    def can_shelve(self, instance): # pylint: disable=unused-argument
        return False
    def unshelve(self, instance, count_override=None, size_override=None, type_override=None):
        raise NotImplementedError()

    # storage/buckets
    def create_bucket(self, name):
        raise NotImplementedError()
    def delete_bucket(self, name):
        raise NotImplementedError()
    def authorize_bucket(self, cluster, name, retries=3, xmlrpc=None):
        raise NotImplementedError()

    # networking
    def get_default_router(self, network=None):
        '''Get default route address

            Arguments:
                network (str): network name (optional if given to constructor)
            Returns:
                str: address of default router
        '''
        return self._get_network_data(network)['gateway']

    def get_dns_servers(self, network=None):
        '''Get DNS server addresses

            Arguments:
                network (str): network name (optional if given to constructor)
            Returns:
                [str]: list of DNS server addresses
        '''
        try:
            return self._get_network_data(network)['dns'].split()
        except Exception as e:
            log.debug(e)
            return self.DNS_SERVERS

    def get_ntp_servers(self):
        '''Get NTP server addresses
            Returns:
                [str]: list of NTP server addresses
        '''
        return self.NTP_SERVERS

    def get_available_addresses(self, count=1, contiguous=False, addr_range=None, in_use=None):
        '''Returns a list of available addresses for the given range
            Arguments:
                count (int, optional): number of addresses required
                contiguous (bool=False): addresses must be contiguous
                addr_range (str, optional): address range cidr block
                in_use ([str], optional): list of addresses known to be used

            Returns:
                ([], str): tuple of address list and netmask str

            Raises: vFXTConfigurationException
        '''
        ipmgr   = self._ip_mgmt_call()
        mask    = self._get_network_data()['network_mask']
        addrs   = None
        if contiguous:
            addrs = ipmgr.allocate(self.user, count, self.network)
        else:
            addrs = ipmgr.allocate_noncontiguous(self.user, count, self.network)
        return (addrs, mask)

    def add_instance_address(self, instance, address, **options):
        raise NotImplementedError()

    def remove_instance_address(self, address):
        raise NotImplementedError()

    def in_use_addresses(self, cidr_block):
        '''Return a list of in use addresses within the specified cidr

            Arguments:
                cidr_block (str)
        '''
        c         = vFXT.Cidr(cidr_block)
        ipmgr     = self._ip_mgmt_call()
        addresses = set([_[0] for _ in ipmgr.dumpinfo() if c.contains(_[0])])
        return sorted(addresses)

    def instance_in_use_addresses(self, instance, category='all'): # pylint: disable=unused-argument
        '''Get the in use addresses for the instance

            Arguments:
                instance: backend instance
                category (str): all, instance, routes

        '''
        data = self._get_instance_xml_data(instance)
        addresses = set([data[_] for _ in sorted(data.keys()) if _.startswith('eth') and _.endswith('_ip') and data[_]])
        addresses.update([_.ip for _ in instance.template.nics]) # XXX redundant or the correct way?
        return sorted(addresses)

    def export(self):
        '''Export the service object in an easy to serialize format
            Returns:
                {}: serializable dictionary
        '''
        return {
            'username':self.user,
            'password':self.passwd,
            'proxy':self.proxy,
            'network':self.network,
        }

    @classmethod
    def _get_xml_data(cls, element, data):
        '''Dict'ify xml.etree.ElementTree
        '''
        key = element.tag.lower()
        data[key] = element.text
        for child in element.getchildren():
            cls._get_xml_data(child, data)

    @classmethod
    def _get_instance_xml_data(cls, instance):
        ''' return a dict of the instance xml data
        '''
        data = {}
        cls._get_xml_data(instance.xml, data)
        return data

    def _pool(self, pool_class, mine=False, start=-1, end=-1):
        ''' OpenNebula *pool* class abstraction helper
        '''
        # Filtering api:
        #    Where filter is
        #        -3: Connected user's resources
        #        -2: All resources
        #        -1: Connected user's and his group's resources
        #         > = 0: UID User's Resources
        #
        conn = self.connection()
        pool = pool_class(conn)
        pool.info(-3 if mine else -2, start, end)
        return pool

    def _list_images(self, mine=False):
        ''' helper to list images
        '''
        return self._pool(oca.ImagePool, mine)

    def _list_templates(self, mine=False):
        ''' helper to list templates
        '''
        return self._pool(oca.VmTemplatePool, mine)

    def _list_networks(self, mine=False):
        ''' helper to list networks
        '''
        return self._pool(oca.VirtualNetworkPool, mine)

    def _get_network_data(self, network=None):
        ''' get network data for named network or the service default network
        '''
        network = network or self.network
        if not network:
            raise vFXTConfigurationException("Must provide a network or have a predefined network")
        networks = self._list_networks()
        networks = [_ for _ in self._list_networks() if _.name == network]
        if not networks:
            raise vFXTConfigurationException("No such network")
        n = networks[0]
        data = {}
        self._get_xml_data(n.xml, data)
        return data

    def _get_network_cidr(self, network=None):
        ''' get the network cidr for the named network or the service default network
        '''
        data = self._get_network_data(network)
        mask = data['network_mask']
        addr = data['network_address']
        return '{}/{}'.format(addr, vFXT.Cidr.to_prefix(vFXT.Cidr.from_address(mask)))

    def _list_hosts(self, mine=False):
        ''' list hosts helper
        '''
        return self._pool(oca.HostPool, mine)

    def _ip_mgmt_call(self, user=None, password=''):
        ''' return a handle for the ip manager xmlrpc service
        '''
        user = user or self.user
        password = password or self.passwd
        ssl_context = ssl._create_unverified_context()
        ip_mgmt_url = "https://{}:{}@ipmanager.avere.net:8443".format(urllib.quote_plus(user), urllib.quote_plus(password))
        s = xmlrpclib.ServerProxy(ip_mgmt_url, verbose=False, use_datetime=True, allow_none=True, context=ssl_context)
        return s


def main():
    ''' avereone utility
    '''
    def _validate_ip(addr):
        ''' ip address validation
        '''
        try:
            socket.inet_aton(addr)
            return addr
        except socket.error:
            raise argparse.ArgumentTypeError("malformed IP address: {}".format(addr))

    epilog = '''EXAMPLES:
Create a cluster
avereone.py --network onenet --create-cluster --cluster-name janedoe-cluster-1 --admin-password secret

Destroy a cluster:
avereone.py --network onenet --destroy-cluster --cluster-name janedoe-cluster-1 --admin-password secret --management-address 10.1.1.1

Add a node to a cluster:
avereone.py --network onenet --add-nodes 1 --cluster-name janedoe-cluster-1 --admin-password secret --management-address 10.1.1.1

List your virtual machines:
avereone.py --network onenet --list'''

    def _load_cluster(args):
        ''' helper to load cluster based on cli args
        '''
        if not (all([args.cluster_name, args.admin_password]) or all([args.management_address, args.admin_password])):
            log.error("--cluster-name/--admin-password or --management-address/--admin-password required")
            parser.exit(1)

        # we only see our users instances
        if args.cluster_name:
            instance_name_re = re.compile(r'^{}\-[0-9]$'.format(re.escape(args.cluster_name)))
            nodes = [_ for _ in [ServiceInstance(service, instance=_) for _ in service.find_instances()] if instance_name_re.search(_.name())]
            if not nodes:
                log.error("Did not find any nodes for {}".format(args.cluster_name))
                parser.exit(1)
            return Cluster(service, nodes=nodes, mgmt_ip=args.management_address or nodes[0].ip(), admin_password=args.admin_password)
        if all([args.management_address, args.admin_password]):
            return Cluster.load(service, mgmt_ip=args.management_address, admin_password=args.admin_password)

    parser = argparse.ArgumentParser(description="OpenNebula vFXT integration", version=vFXT.__version__, epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
    auth_args = parser.add_argument_group("Authentication options", "OpenNebula authentication and configuration information.")
    auth_args.add_argument("--username", help="OpenNebula user username (defaults to {})".format(getpass.getuser()), type=str, default=getpass.getuser())
    auth_args.add_argument("--password", help="OpenNebula user password (prompts if not provided)", type=str)
    auth_args.add_argument('--network', help='OpenNebula virtual network name', type=str, required=True)
    auth_args.add_argument('--template', help='OpenNebula machine template name (default to Avere KVM SIM)', type=str, default='Avere KVM SIM')

    action_opts = parser.add_mutually_exclusive_group(required=True)
    action_opts.add_argument('--create-cluster', help='Create a new cluster', action="store_true")
    action_opts.add_argument('--destroy-cluster', help='Destroy a cluster', action="store_true")
    action_opts.add_argument('--add-nodes', help='Add nodes to a cluster', type=int, default=0)
    action_opts.add_argument('--list', help='List your current virtual machines', action="store_true")
    action_opts.add_argument('--interact', help='Interactive python shell', action="store_true")

    cluster_opts = parser.add_argument_group("Cluster options")
    cluster_opts.add_argument("--cluster-name", help="Name for the cluster")
    cluster_opts.add_argument("--admin-password", help="Admin password for the cluster")
    cluster_opts.add_argument("--nodes", help="(Optional) Number of nodes to create in the cluster (default 3)", type=int, default=3)
    cluster_opts.add_argument("--vserver-name", help="(Optional) Name of the vserver (default to vserver1)", type=str, default="vserver1")

    network_opts = parser.add_argument_group("Network options", "These are optional.  If no values are provided IP addresses will be queried from the IT IP management service.")
    network_opts.add_argument("--management-address", help="(Optional) IP address for management of the cluster", metavar="IP_ADDR", type=_validate_ip)
    network_opts.add_argument("--first-cluster-address", help="(Optional) First cluster range IP address", metavar="IP_ADDR", type=_validate_ip)
    network_opts.add_argument("--last-cluster-address", help="(Optional) Last cluster range IP address", metavar="IP_ADDR", type=_validate_ip)
    network_opts.add_argument("--vserver-netmask", help="(Optional) Netmask of the vserver", metavar="NET_MASK", type=_validate_ip)
    network_opts.add_argument("--first-vserver-address", help="(Optional) First vserver range IP address", metavar="IP_ADDR", type=_validate_ip)
    network_opts.add_argument("--last-vserver-address", help="(Optional) Last vserver range IP address", metavar="IP_ADDR", type=_validate_ip)

    general_args = parser.add_argument_group("General options")
    general_args.add_argument('--proxy-uri', help='Proxy resource for API calls, example http://user:pass@172.16.16.20:8080/', metavar="URL", type=str)
    general_args.add_argument('--skip-cleanup', help='Do not destroy on failures', action="store_true")
    general_args.add_argument('--debug', help='Debug output', action="store_true")

    args = parser.parse_args()

    logging_format='%(asctime)s - %(name)s:%(levelname)s - %(message)s'
    logging_datefmt='%Y-%m-%dT%H:%M:%S%z'
    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format=logging_format, datefmt=logging_datefmt, level=logging_level)

    if not args.password:
        args.password = getpass.getpass("Enter the OpenNebula passsword for {}: ".format(args.username))

    service = Service(args.network, args.username, args.password, proxy=args.proxy_uri)

    if args.network not in [_.name for _ in service._list_networks()]:
        log.error("{} is not a valid network name.".format(args.network))
        parser.exit(1)

    if args.create_cluster:
        if not all([args.cluster_name, args.admin_password]):
            log.error("--cluster-name and  --admin-password are required")
            parser.exit(1)

        if args.template not in [_.name for _ in service._list_templates()]:
            log.error("{} is not a valid template name.".format(args.template))
            parser.exit(1)

        log.info("Creating cluster {}".format(args.cluster_name))
        try:
            cluster = Cluster.create(service, args.template,
                args.cluster_name,
                args.admin_password,
                wait_for_state='red', # ip conflicts or other reasons
                skip_cleanup=args.skip_cleanup,
                join_instance_address=True,
                join_wait=700 + (700 * math.log(args.nodes)),
                size=args.nodes,
                management_address=args.management_address,
                address_range_start=args.first_cluster_address,
                address_range_end=args.last_cluster_address)

            log.info("{} version {}".format(cluster.name, cluster.xmlrpc().cluster.get()['activeImage']))
            log.info("{} management address: {}".format(cluster.name, cluster.mgmt_ip))
            log.info("{} nodes: {}".format(cluster.name, ' '.join([n.name() for n in cluster.nodes])))
            cluster.add_vserver('vserver1', netmask=args.vserver_netmask, start_address=args.first_vserver_address, end_address=args.last_vserver_address)
            log.info("Complete")
        except Exception as e:
            if args.debug:
                log.exception(e)
            log.error("Failed to create cluster: {}".format(e))
            parser.exit(1)

    elif args.destroy_cluster:
        cluster = _load_cluster(args)
        log.info("Destroying cluster with nodes {}".format(', '.join([_.name() for _ in cluster.nodes])))
        try:
            if all([cluster.mgmt_ip, cluster.admin_password]):
                addresses = cluster.in_use_addresses()
                service._ip_mgmt_call().release(addresses)
                # TODO dns de-registration for mgmt, cluster, and vserver, addresses
                # ipmgr.dnsdel(<ip>, <hostname>)
            cluster.destroy(quick_destroy=True)
            log.info("Complete")
        except Exception as e:
            if args.debug:
                log.exception(e)
            log.error("Failed to destroy cluster: {}".format(e))
            parser.exit(1)

    elif args.interact:
        local=globals(); local.update(locals())
        banner = "\n--- Service object available as 'service' ---\n"
        try:
            from IPython import start_ipython
            print banner
            start_ipython(argv=['--classic', '--no-banner'], user_ns=local)
        except ImportError:
            from code import interact
            interact(local=local)
    elif args.list:
        for instance in service.find_instances():
            print "{} {}".format(service.instance_id(instance), service.name(instance))
    elif args.add_nodes:
        cluster = _load_cluster(args)
        log.info("Extending cluster with {} nodes".format(args.add_nodes))
        try:
            cluster.add_nodes(args.add_nodes)
            log.info("{} version {}".format(cluster.name, cluster.xmlrpc().cluster.get()['activeImage']))
            log.info("{} management address: {}".format(cluster.name, cluster.mgmt_ip))
            log.info("{} nodes: {}".format(cluster.name, ' '.join([n.name() for n in cluster.nodes])))
            log.info("Complete")
        except Exception as e:
            if args.debug:
                log.exception(e)
            log.error("Failed to destroy cluster: {}".format(e))
            parser.exit(1)

if __name__ == '__main__':
    main()
