# coding: utf-8

"""
    OpenShift API (with Kubernetes)

    OpenShift provides builds, application lifecycle, image content management, and administrative policy on top of Kubernetes. The API allows consistent management of those objects.  All API operations are authenticated via an Authorization bearer token that is provided for service accounts as a generated secret (in JWT form) or via the native OAuth endpoint located at /oauth/authorize. Core infrastructure components may use client certificates that require no authentication.  All API operations return a 'resourceVersion' string that represents the version of the object in the underlying storage. The standard LIST operation performs a snapshot read of the underlying objects, returning a resourceVersion representing a consistent version of the listed objects. The WATCH operation allows all updates to a set of objects after the provided resourceVersion to be observed by a client. By listing and beginning a watch from the returned resourceVersion, clients may observe a consistent view of the state of one or more objects. Note that WATCH always returns the update after the provided resourceVersion. Watch may be extended a limited time in the past - using etcd 2 the watch window is 1000 events (which on a large cluster may only be a few tens of seconds) so clients must explicitly handle the \"watch to old error\" by re-listing.  Objects are divided into two rough categories - those that have a lifecycle and must reflect the state of the cluster, and those that have no state. Objects with lifecycle typically have three main sections:  * 'metadata' common to all objects * a 'spec' that represents the desired state * a 'status' that represents how much of the desired state is reflected on   the cluster at the current time  Objects that have no state have 'metadata' but may lack a 'spec' or 'status' section.  Objects are divided into those that are namespace scoped (only exist inside of a namespace) and those that are cluster scoped (exist outside of a namespace). A namespace scoped resource will be deleted when the namespace is deleted and cannot be created if the namespace has not yet been created or is in the process of deletion. Cluster scoped resources are typically only accessible to admins - resources like nodes, persistent volumes, and cluster policy.  All objects have a schema that is a combination of the 'kind' and 'apiVersion' fields. This schema is additive only for any given version - no backwards incompatible changes are allowed without incrementing the apiVersion. The server will return and accept a number of standard responses that share a common schema - for instance, the common error type is 'metav1.Status' (described below) and will be returned on any error from the API server.  The API is available in multiple serialization formats - the default is JSON (Accept: application/json and Content-Type: application/json) but clients may also use YAML (application/yaml) or the native Protobuf schema (application/vnd.kubernetes.protobuf). Note that the format of the WATCH API call is slightly different - for JSON it returns newline delimited objects while for Protobuf it returns length-delimited frames (4 bytes in network-order) that contain a 'versioned.Watch' Protobuf object.  See the OpenShift documentation at https://docs.openshift.org for more information. 

    OpenAPI spec version: latest
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class V1ClusterRole(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'aggregation_rule': 'V1AggregationRule',
        'api_version': 'str',
        'kind': 'str',
        'metadata': 'V1ObjectMeta',
        'rules': 'list[V1PolicyRule]'
    }

    attribute_map = {
        'aggregation_rule': 'aggregationRule',
        'api_version': 'apiVersion',
        'kind': 'kind',
        'metadata': 'metadata',
        'rules': 'rules'
    }

    def __init__(self, aggregation_rule=None, api_version=None, kind=None, metadata=None, rules=None):
        """
        V1ClusterRole - a model defined in Swagger
        """

        self._aggregation_rule = None
        self._api_version = None
        self._kind = None
        self._metadata = None
        self._rules = None
        self.discriminator = None

        if aggregation_rule is not None:
          self.aggregation_rule = aggregation_rule
        if api_version is not None:
          self.api_version = api_version
        if kind is not None:
          self.kind = kind
        if metadata is not None:
          self.metadata = metadata
        self.rules = rules

    @property
    def aggregation_rule(self):
        """
        Gets the aggregation_rule of this V1ClusterRole.
        AggregationRule is an optional field that describes how to build the Rules for this ClusterRole. If AggregationRule is set, then the Rules are controller managed and direct changes to Rules will be stomped by the controller.

        :return: The aggregation_rule of this V1ClusterRole.
        :rtype: V1AggregationRule
        """
        return self._aggregation_rule

    @aggregation_rule.setter
    def aggregation_rule(self, aggregation_rule):
        """
        Sets the aggregation_rule of this V1ClusterRole.
        AggregationRule is an optional field that describes how to build the Rules for this ClusterRole. If AggregationRule is set, then the Rules are controller managed and direct changes to Rules will be stomped by the controller.

        :param aggregation_rule: The aggregation_rule of this V1ClusterRole.
        :type: V1AggregationRule
        """

        self._aggregation_rule = aggregation_rule

    @property
    def api_version(self):
        """
        Gets the api_version of this V1ClusterRole.
        APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#resources

        :return: The api_version of this V1ClusterRole.
        :rtype: str
        """
        return self._api_version

    @api_version.setter
    def api_version(self, api_version):
        """
        Sets the api_version of this V1ClusterRole.
        APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#resources

        :param api_version: The api_version of this V1ClusterRole.
        :type: str
        """

        self._api_version = api_version

    @property
    def kind(self):
        """
        Gets the kind of this V1ClusterRole.
        Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#types-kinds

        :return: The kind of this V1ClusterRole.
        :rtype: str
        """
        return self._kind

    @kind.setter
    def kind(self, kind):
        """
        Sets the kind of this V1ClusterRole.
        Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#types-kinds

        :param kind: The kind of this V1ClusterRole.
        :type: str
        """

        self._kind = kind

    @property
    def metadata(self):
        """
        Gets the metadata of this V1ClusterRole.
        Standard object's metadata.

        :return: The metadata of this V1ClusterRole.
        :rtype: V1ObjectMeta
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """
        Sets the metadata of this V1ClusterRole.
        Standard object's metadata.

        :param metadata: The metadata of this V1ClusterRole.
        :type: V1ObjectMeta
        """

        self._metadata = metadata

    @property
    def rules(self):
        """
        Gets the rules of this V1ClusterRole.
        Rules holds all the PolicyRules for this ClusterRole

        :return: The rules of this V1ClusterRole.
        :rtype: list[V1PolicyRule]
        """
        return self._rules

    @rules.setter
    def rules(self, rules):
        """
        Sets the rules of this V1ClusterRole.
        Rules holds all the PolicyRules for this ClusterRole

        :param rules: The rules of this V1ClusterRole.
        :type: list[V1PolicyRule]
        """
        if rules is None:
            raise ValueError("Invalid value for `rules`, must not be `None`")

        self._rules = rules

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, V1ClusterRole):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
