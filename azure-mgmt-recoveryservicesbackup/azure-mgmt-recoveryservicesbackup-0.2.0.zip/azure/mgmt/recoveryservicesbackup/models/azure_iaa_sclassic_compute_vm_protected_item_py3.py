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

from .azure_iaa_svm_protected_item_py3 import AzureIaaSVMProtectedItem


class AzureIaaSClassicComputeVMProtectedItem(AzureIaaSVMProtectedItem):
    """IaaS VM workload-specific backup item representing the Classic Compute VM.

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
    :param friendly_name: Friendly name of the VM represented by this backup
     item.
    :type friendly_name: str
    :param virtual_machine_id: Fully qualified ARM ID of the virtual machine
     represented by this item.
    :type virtual_machine_id: str
    :param protection_status: Backup status of this backup item.
    :type protection_status: str
    :param protection_state: Backup state of this backup item. Possible values
     include: 'Invalid', 'IRPending', 'Protected', 'ProtectionError',
     'ProtectionStopped', 'ProtectionPaused'
    :type protection_state: str or
     ~azure.mgmt.recoveryservicesbackup.models.ProtectionState
    :param health_status: Health status of protected item. Possible values
     include: 'Passed', 'ActionRequired', 'ActionSuggested', 'Invalid'
    :type health_status: str or
     ~azure.mgmt.recoveryservicesbackup.models.HealthStatus
    :param health_details: Health details on this backup item.
    :type health_details:
     list[~azure.mgmt.recoveryservicesbackup.models.AzureIaaSVMHealthDetails]
    :param last_backup_status: Last backup operation status.
    :type last_backup_status: str
    :param last_backup_time: Timestamp of the last backup operation on this
     backup item.
    :type last_backup_time: datetime
    :param protected_item_data_id: Data ID of the protected item.
    :type protected_item_data_id: str
    :param extended_info: Additional information for this backup item.
    :type extended_info:
     ~azure.mgmt.recoveryservicesbackup.models.AzureIaaSVMProtectedItemExtendedInfo
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
        'friendly_name': {'key': 'friendlyName', 'type': 'str'},
        'virtual_machine_id': {'key': 'virtualMachineId', 'type': 'str'},
        'protection_status': {'key': 'protectionStatus', 'type': 'str'},
        'protection_state': {'key': 'protectionState', 'type': 'str'},
        'health_status': {'key': 'healthStatus', 'type': 'str'},
        'health_details': {'key': 'healthDetails', 'type': '[AzureIaaSVMHealthDetails]'},
        'last_backup_status': {'key': 'lastBackupStatus', 'type': 'str'},
        'last_backup_time': {'key': 'lastBackupTime', 'type': 'iso-8601'},
        'protected_item_data_id': {'key': 'protectedItemDataId', 'type': 'str'},
        'extended_info': {'key': 'extendedInfo', 'type': 'AzureIaaSVMProtectedItemExtendedInfo'},
    }

    def __init__(self, *, backup_management_type=None, workload_type=None, container_name: str=None, source_resource_id: str=None, policy_id: str=None, last_recovery_point=None, backup_set_name: str=None, friendly_name: str=None, virtual_machine_id: str=None, protection_status: str=None, protection_state=None, health_status=None, health_details=None, last_backup_status: str=None, last_backup_time=None, protected_item_data_id: str=None, extended_info=None, **kwargs) -> None:
        super(AzureIaaSClassicComputeVMProtectedItem, self).__init__(backup_management_type=backup_management_type, workload_type=workload_type, container_name=container_name, source_resource_id=source_resource_id, policy_id=policy_id, last_recovery_point=last_recovery_point, backup_set_name=backup_set_name, friendly_name=friendly_name, virtual_machine_id=virtual_machine_id, protection_status=protection_status, protection_state=protection_state, health_status=health_status, health_details=health_details, last_backup_status=last_backup_status, last_backup_time=last_backup_time, protected_item_data_id=protected_item_data_id, extended_info=extended_info, **kwargs)
        self.protected_item_type = 'Microsoft.ClassicCompute/virtualMachines'
