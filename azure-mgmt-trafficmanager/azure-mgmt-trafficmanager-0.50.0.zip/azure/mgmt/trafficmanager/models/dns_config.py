# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class DnsConfig(Model):
    """Class containing DNS settings in a Traffic Manager profile.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :param relative_name: The relative DNS name provided by this Traffic
     Manager profile. This value is combined with the DNS domain name used by
     Azure Traffic Manager to form the fully-qualified domain name (FQDN) of
     the profile.
    :type relative_name: str
    :ivar fqdn: The fully-qualified domain name (FQDN) of the Traffic Manager
     profile. This is formed from the concatenation of the RelativeName with
     the DNS domain used by Azure Traffic Manager.
    :vartype fqdn: str
    :param ttl: The DNS Time-To-Live (TTL), in seconds. This informs the local
     DNS resolvers and DNS clients how long to cache DNS responses provided by
     this Traffic Manager profile.
    :type ttl: long
    """

    _validation = {
        'fqdn': {'readonly': True},
    }

    _attribute_map = {
        'relative_name': {'key': 'relativeName', 'type': 'str'},
        'fqdn': {'key': 'fqdn', 'type': 'str'},
        'ttl': {'key': 'ttl', 'type': 'long'},
    }

    def __init__(self, **kwargs):
        super(DnsConfig, self).__init__(**kwargs)
        self.relative_name = kwargs.get('relative_name', None)
        self.fqdn = None
        self.ttl = kwargs.get('ttl', None)
