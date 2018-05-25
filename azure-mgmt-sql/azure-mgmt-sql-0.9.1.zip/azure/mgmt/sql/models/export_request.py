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


class ExportRequest(Model):
    """Export database parameters.

    All required parameters must be populated in order to send to Azure.

    :param storage_key_type: Required. The type of the storage key to use.
     Possible values include: 'StorageAccessKey', 'SharedAccessKey'
    :type storage_key_type: str or ~azure.mgmt.sql.models.StorageKeyType
    :param storage_key: Required. The storage key to use.  If storage key type
     is SharedAccessKey, it must be preceded with a "?."
    :type storage_key: str
    :param storage_uri: Required. The storage uri to use.
    :type storage_uri: str
    :param administrator_login: Required. The name of the SQL administrator.
    :type administrator_login: str
    :param administrator_login_password: Required. The password of the SQL
     administrator.
    :type administrator_login_password: str
    :param authentication_type: The authentication type. Possible values
     include: 'SQL', 'ADPassword'. Default value: "SQL" .
    :type authentication_type: str or
     ~azure.mgmt.sql.models.AuthenticationType
    """

    _validation = {
        'storage_key_type': {'required': True},
        'storage_key': {'required': True},
        'storage_uri': {'required': True},
        'administrator_login': {'required': True},
        'administrator_login_password': {'required': True},
    }

    _attribute_map = {
        'storage_key_type': {'key': 'storageKeyType', 'type': 'StorageKeyType'},
        'storage_key': {'key': 'storageKey', 'type': 'str'},
        'storage_uri': {'key': 'storageUri', 'type': 'str'},
        'administrator_login': {'key': 'administratorLogin', 'type': 'str'},
        'administrator_login_password': {'key': 'administratorLoginPassword', 'type': 'str'},
        'authentication_type': {'key': 'authenticationType', 'type': 'AuthenticationType'},
    }

    def __init__(self, **kwargs):
        super(ExportRequest, self).__init__(**kwargs)
        self.storage_key_type = kwargs.get('storage_key_type', None)
        self.storage_key = kwargs.get('storage_key', None)
        self.storage_uri = kwargs.get('storage_uri', None)
        self.administrator_login = kwargs.get('administrator_login', None)
        self.administrator_login_password = kwargs.get('administrator_login_password', None)
        self.authentication_type = kwargs.get('authentication_type', "SQL")
