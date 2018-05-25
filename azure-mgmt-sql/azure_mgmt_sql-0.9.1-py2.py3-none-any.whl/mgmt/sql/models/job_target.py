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


class JobTarget(Model):
    """A job target, for example a specific database or a container of databases
    that is evaluated during job execution.

    All required parameters must be populated in order to send to Azure.

    :param membership_type: Whether the target is included or excluded from
     the group. Possible values include: 'Include', 'Exclude'. Default value:
     "Include" .
    :type membership_type: str or
     ~azure.mgmt.sql.models.JobTargetGroupMembershipType
    :param type: Required. The target type. Possible values include:
     'TargetGroup', 'SqlDatabase', 'SqlElasticPool', 'SqlShardMap', 'SqlServer'
    :type type: str or ~azure.mgmt.sql.models.JobTargetType
    :param server_name: The target server name.
    :type server_name: str
    :param database_name: The target database name.
    :type database_name: str
    :param elastic_pool_name: The target elastic pool name.
    :type elastic_pool_name: str
    :param shard_map_name: The target shard map.
    :type shard_map_name: str
    :param refresh_credential: The resource ID of the credential that is used
     during job execution to connect to the target and determine the list of
     databases inside the target.
    :type refresh_credential: str
    """

    _validation = {
        'type': {'required': True},
    }

    _attribute_map = {
        'membership_type': {'key': 'membershipType', 'type': 'JobTargetGroupMembershipType'},
        'type': {'key': 'type', 'type': 'str'},
        'server_name': {'key': 'serverName', 'type': 'str'},
        'database_name': {'key': 'databaseName', 'type': 'str'},
        'elastic_pool_name': {'key': 'elasticPoolName', 'type': 'str'},
        'shard_map_name': {'key': 'shardMapName', 'type': 'str'},
        'refresh_credential': {'key': 'refreshCredential', 'type': 'str'},
    }

    def __init__(self, **kwargs):
        super(JobTarget, self).__init__(**kwargs)
        self.membership_type = kwargs.get('membership_type', "Include")
        self.type = kwargs.get('type', None)
        self.server_name = kwargs.get('server_name', None)
        self.database_name = kwargs.get('database_name', None)
        self.elastic_pool_name = kwargs.get('elastic_pool_name', None)
        self.shard_map_name = kwargs.get('shard_map_name', None)
        self.refresh_credential = kwargs.get('refresh_credential', None)
