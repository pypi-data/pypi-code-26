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


class EndpointPropertiesUpdateParametersDeliveryPolicy(Model):
    """A policy that specifies the delivery rules to be used for an endpoint.

    All required parameters must be populated in order to send to Azure.

    :param description: User-friendly description of the policy.
    :type description: str
    :param rules: Required. A list of the delivery rules.
    :type rules: list[~azure.mgmt.cdn.models.DeliveryRule]
    """

    _validation = {
        'rules': {'required': True},
    }

    _attribute_map = {
        'description': {'key': 'description', 'type': 'str'},
        'rules': {'key': 'rules', 'type': '[DeliveryRule]'},
    }

    def __init__(self, *, rules, description: str=None, **kwargs) -> None:
        super(EndpointPropertiesUpdateParametersDeliveryPolicy, self).__init__(**kwargs)
        self.description = description
        self.rules = rules
