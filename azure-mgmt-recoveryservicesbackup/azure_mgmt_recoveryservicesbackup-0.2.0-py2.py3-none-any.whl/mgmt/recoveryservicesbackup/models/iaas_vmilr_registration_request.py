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

from .ilr_request import ILRRequest


class IaasVMILRRegistrationRequest(ILRRequest):
    """Restore files/folders from a backup copy of IaaS VM.

    All required parameters must be populated in order to send to Azure.

    :param object_type: Required. Constant filled by server.
    :type object_type: str
    :param recovery_point_id: ID of the IaaS VM backup copy from where the
     files/folders have to be restored.
    :type recovery_point_id: str
    :param virtual_machine_id: Fully qualified ARM ID of the virtual machine
     whose the files / folders have to be restored.
    :type virtual_machine_id: str
    :param initiator_name: iSCSI initiator name.
    :type initiator_name: str
    :param renew_existing_registration: Whether to renew existing registration
     with the iSCSI server.
    :type renew_existing_registration: bool
    """

    _validation = {
        'object_type': {'required': True},
    }

    _attribute_map = {
        'object_type': {'key': 'objectType', 'type': 'str'},
        'recovery_point_id': {'key': 'recoveryPointId', 'type': 'str'},
        'virtual_machine_id': {'key': 'virtualMachineId', 'type': 'str'},
        'initiator_name': {'key': 'initiatorName', 'type': 'str'},
        'renew_existing_registration': {'key': 'renewExistingRegistration', 'type': 'bool'},
    }

    def __init__(self, **kwargs):
        super(IaasVMILRRegistrationRequest, self).__init__(**kwargs)
        self.recovery_point_id = kwargs.get('recovery_point_id', None)
        self.virtual_machine_id = kwargs.get('virtual_machine_id', None)
        self.initiator_name = kwargs.get('initiator_name', None)
        self.renew_existing_registration = kwargs.get('renew_existing_registration', None)
        self.object_type = 'IaasVMILRRegistrationRequest'
