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

from .tracked_resource import TrackedResource


class ElasticPool(TrackedResource):
    """An elastic pool.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    All required parameters must be populated in order to send to Azure.

    :ivar id: Resource ID.
    :vartype id: str
    :ivar name: Resource name.
    :vartype name: str
    :ivar type: Resource type.
    :vartype type: str
    :param tags: Resource tags.
    :type tags: dict[str, str]
    :param location: Required. Resource location.
    :type location: str
    :param sku:
    :type sku: ~azure.mgmt.sql.models.Sku
    :ivar kind: Kind of elastic pool. This is metadata used for the Azure
     portal experience.
    :vartype kind: str
    :ivar state: The state of the elastic pool. Possible values include:
     'Creating', 'Ready', 'Disabled'
    :vartype state: str or ~azure.mgmt.sql.models.ElasticPoolState
    :ivar creation_date: The creation date of the elastic pool (ISO8601
     format).
    :vartype creation_date: datetime
    :param max_size_bytes: The storage limit for the database elastic pool in
     bytes.
    :type max_size_bytes: long
    :param per_database_settings: The per database settings for the elastic
     pool.
    :type per_database_settings:
     ~azure.mgmt.sql.models.ElasticPoolPerDatabaseSettings
    :param zone_redundant: Whether or not this elastic pool is zone redundant,
     which means the replicas of this elastic pool will be spread across
     multiple availability zones.
    :type zone_redundant: bool
    :param license_type: The license type to apply for this elastic pool.
     Possible values include: 'LicenseIncluded', 'BasePrice'
    :type license_type: str or ~azure.mgmt.sql.models.ElasticPoolLicenseType
    """

    _validation = {
        'id': {'readonly': True},
        'name': {'readonly': True},
        'type': {'readonly': True},
        'location': {'required': True},
        'kind': {'readonly': True},
        'state': {'readonly': True},
        'creation_date': {'readonly': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'name': {'key': 'name', 'type': 'str'},
        'type': {'key': 'type', 'type': 'str'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'location': {'key': 'location', 'type': 'str'},
        'sku': {'key': 'sku', 'type': 'Sku'},
        'kind': {'key': 'kind', 'type': 'str'},
        'state': {'key': 'properties.state', 'type': 'str'},
        'creation_date': {'key': 'properties.creationDate', 'type': 'iso-8601'},
        'max_size_bytes': {'key': 'properties.maxSizeBytes', 'type': 'long'},
        'per_database_settings': {'key': 'properties.perDatabaseSettings', 'type': 'ElasticPoolPerDatabaseSettings'},
        'zone_redundant': {'key': 'properties.zoneRedundant', 'type': 'bool'},
        'license_type': {'key': 'properties.licenseType', 'type': 'str'},
    }

    def __init__(self, **kwargs):
        super(ElasticPool, self).__init__(**kwargs)
        self.sku = kwargs.get('sku', None)
        self.kind = None
        self.state = None
        self.creation_date = None
        self.max_size_bytes = kwargs.get('max_size_bytes', None)
        self.per_database_settings = kwargs.get('per_database_settings', None)
        self.zone_redundant = kwargs.get('zone_redundant', None)
        self.license_type = kwargs.get('license_type', None)
