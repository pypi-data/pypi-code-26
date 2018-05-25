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


class ProtectedItem(Model):
    """Base class for backup items.

    You probably want to use the sub-classes and not this class directly. Known
    sub-classes are: AzureFileshareProtectedItem, AzureIaaSVMProtectedItem,
    AzureSqlProtectedItem, AzureVmWorkloadSQLDatabaseProtectedItem,
    DPMProtectedItem, GenericProtectedItem, MabFileFolderProtectedItem

    All required parameters must be populated in order to send to Azure.

    :param backup_management_type: Type of backup managemenent for the backed
     up item. Possible values include: 'Invalid', 'AzureIaasVM', 'MAB', 'DPM',
     'AzureBackupServer', 'AzureSql', 'AzureStorage', 'AzureWorkload',
     'DefaultBackup'
    :type backup_management_type: str or
     ~azure.mgmt.recoveryservicesbackup.models.BackupManagementType
    :param workload_type: Type of workload this item represents. Possible
     values include: 'Invalid', 'VM', 'FileFolder', 'AzureSqlDb', 'SQLDB',
     'Exchange', 'Sharepoint', 'VMwareVM', 'SystemState', 'Client',
     'GenericDataSource', 'SQLDataBase', 'AzureFileShare'
    :type workload_type: str or
     ~azure.mgmt.recoveryservicesbackup.models.DataSourceType
    :param container_name: Unique name of container
    :type container_name: str
    :param source_resource_id: ARM ID of the resource to be backed up.
    :type source_resource_id: str
    :param policy_id: ID of the backup policy with which this item is backed
     up.
    :type policy_id: str
    :param last_recovery_point: Timestamp when the last (latest) backup copy
     was created for this backup item.
    :type last_recovery_point: datetime
    :param backup_set_name: Name of the backup set the backup item belongs to
    :type backup_set_name: str
    :param protected_item_type: Required. Constant filled by server.
    :type protected_item_type: str
    """

    _validation = {
        'protected_item_type': {'required': True},
    }

    _attribute_map = {
        'backup_management_type': {'key': 'backupManagementType', 'type': 'str'},
        'workload_type': {'key': 'workloadType', 'type': 'str'},
        'container_name': {'key': 'containerName', 'type': 'str'},
        'source_resource_id': {'key': 'sourceResourceId', 'type': 'str'},
        'policy_id': {'key': 'policyId', 'type': 'str'},
        'last_recovery_point': {'key': 'lastRecoveryPoint', 'type': 'iso-8601'},
        'backup_set_name': {'key': 'backupSetName', 'type': 'str'},
        'protected_item_type': {'key': 'protectedItemType', 'type': 'str'},
    }

    _subtype_map = {
        'protected_item_type': {'AzureFileShareProtectedItem': 'AzureFileshareProtectedItem', 'AzureIaaSVMProtectedItem': 'AzureIaaSVMProtectedItem', 'Microsoft.Sql/servers/databases': 'AzureSqlProtectedItem', 'AzureVmWorkloadSQLDatabase': 'AzureVmWorkloadSQLDatabaseProtectedItem', 'DPMProtectedItem': 'DPMProtectedItem', 'GenericProtectedItem': 'GenericProtectedItem', 'MabFileFolderProtectedItem': 'MabFileFolderProtectedItem'}
    }

    def __init__(self, *, backup_management_type=None, workload_type=None, container_name: str=None, source_resource_id: str=None, policy_id: str=None, last_recovery_point=None, backup_set_name: str=None, **kwargs) -> None:
        super(ProtectedItem, self).__init__(**kwargs)
        self.backup_management_type = backup_management_type
        self.workload_type = workload_type
        self.container_name = container_name
        self.source_resource_id = source_resource_id
        self.policy_id = policy_id
        self.last_recovery_point = last_recovery_point
        self.backup_set_name = backup_set_name
        self.protected_item_type = None
