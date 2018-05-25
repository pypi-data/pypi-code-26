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

from .proxy_resource import ProxyResource


class LongTermRetentionBackup(ProxyResource):
    """A long term retention backup.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :ivar id: Resource ID.
    :vartype id: str
    :ivar name: Resource name.
    :vartype name: str
    :ivar type: Resource type.
    :vartype type: str
    :ivar server_name: The server name that the backup database belong to.
    :vartype server_name: str
    :ivar server_create_time: The create time of the server.
    :vartype server_create_time: datetime
    :ivar database_name: The name of the database the backup belong to
    :vartype database_name: str
    :ivar database_deletion_time: The delete time of the database
    :vartype database_deletion_time: datetime
    :ivar backup_time: The time the backup was taken
    :vartype backup_time: datetime
    :ivar backup_expiration_time: The time the long term retention backup will
     expire.
    :vartype backup_expiration_time: datetime
    """

    _validation = {
        'id': {'readonly': True},
        'name': {'readonly': True},
        'type': {'readonly': True},
        'server_name': {'readonly': True},
        'server_create_time': {'readonly': True},
        'database_name': {'readonly': True},
        'database_deletion_time': {'readonly': True},
        'backup_time': {'readonly': True},
        'backup_expiration_time': {'readonly': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'name': {'key': 'name', 'type': 'str'},
        'type': {'key': 'type', 'type': 'str'},
        'server_name': {'key': 'properties.serverName', 'type': 'str'},
        'server_create_time': {'key': 'properties.serverCreateTime', 'type': 'iso-8601'},
        'database_name': {'key': 'properties.databaseName', 'type': 'str'},
        'database_deletion_time': {'key': 'properties.databaseDeletionTime', 'type': 'iso-8601'},
        'backup_time': {'key': 'properties.backupTime', 'type': 'iso-8601'},
        'backup_expiration_time': {'key': 'properties.backupExpirationTime', 'type': 'iso-8601'},
    }

    def __init__(self, **kwargs):
        super(LongTermRetentionBackup, self).__init__(**kwargs)
        self.server_name = None
        self.server_create_time = None
        self.database_name = None
        self.database_deletion_time = None
        self.backup_time = None
        self.backup_expiration_time = None
