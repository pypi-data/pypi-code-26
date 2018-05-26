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


class V1RouteIngress(object):
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
        'conditions': 'list[V1RouteIngressCondition]',
        'host': 'str',
        'router_canonical_hostname': 'str',
        'router_name': 'str',
        'wildcard_policy': 'str'
    }

    attribute_map = {
        'conditions': 'conditions',
        'host': 'host',
        'router_canonical_hostname': 'routerCanonicalHostname',
        'router_name': 'routerName',
        'wildcard_policy': 'wildcardPolicy'
    }

    def __init__(self, conditions=None, host=None, router_canonical_hostname=None, router_name=None, wildcard_policy=None):
        """
        V1RouteIngress - a model defined in Swagger
        """

        self._conditions = None
        self._host = None
        self._router_canonical_hostname = None
        self._router_name = None
        self._wildcard_policy = None
        self.discriminator = None

        if conditions is not None:
          self.conditions = conditions
        if host is not None:
          self.host = host
        if router_canonical_hostname is not None:
          self.router_canonical_hostname = router_canonical_hostname
        if router_name is not None:
          self.router_name = router_name
        if wildcard_policy is not None:
          self.wildcard_policy = wildcard_policy

    @property
    def conditions(self):
        """
        Gets the conditions of this V1RouteIngress.
        Conditions is the state of the route, may be empty.

        :return: The conditions of this V1RouteIngress.
        :rtype: list[V1RouteIngressCondition]
        """
        return self._conditions

    @conditions.setter
    def conditions(self, conditions):
        """
        Sets the conditions of this V1RouteIngress.
        Conditions is the state of the route, may be empty.

        :param conditions: The conditions of this V1RouteIngress.
        :type: list[V1RouteIngressCondition]
        """

        self._conditions = conditions

    @property
    def host(self):
        """
        Gets the host of this V1RouteIngress.
        Host is the host string under which the route is exposed; this value is required

        :return: The host of this V1RouteIngress.
        :rtype: str
        """
        return self._host

    @host.setter
    def host(self, host):
        """
        Sets the host of this V1RouteIngress.
        Host is the host string under which the route is exposed; this value is required

        :param host: The host of this V1RouteIngress.
        :type: str
        """

        self._host = host

    @property
    def router_canonical_hostname(self):
        """
        Gets the router_canonical_hostname of this V1RouteIngress.
        CanonicalHostname is the external host name for the router that can be used as a CNAME for the host requested for this route. This value is optional and may not be set in all cases.

        :return: The router_canonical_hostname of this V1RouteIngress.
        :rtype: str
        """
        return self._router_canonical_hostname

    @router_canonical_hostname.setter
    def router_canonical_hostname(self, router_canonical_hostname):
        """
        Sets the router_canonical_hostname of this V1RouteIngress.
        CanonicalHostname is the external host name for the router that can be used as a CNAME for the host requested for this route. This value is optional and may not be set in all cases.

        :param router_canonical_hostname: The router_canonical_hostname of this V1RouteIngress.
        :type: str
        """

        self._router_canonical_hostname = router_canonical_hostname

    @property
    def router_name(self):
        """
        Gets the router_name of this V1RouteIngress.
        Name is a name chosen by the router to identify itself; this value is required

        :return: The router_name of this V1RouteIngress.
        :rtype: str
        """
        return self._router_name

    @router_name.setter
    def router_name(self, router_name):
        """
        Sets the router_name of this V1RouteIngress.
        Name is a name chosen by the router to identify itself; this value is required

        :param router_name: The router_name of this V1RouteIngress.
        :type: str
        """

        self._router_name = router_name

    @property
    def wildcard_policy(self):
        """
        Gets the wildcard_policy of this V1RouteIngress.
        Wildcard policy is the wildcard policy that was allowed where this route is exposed.

        :return: The wildcard_policy of this V1RouteIngress.
        :rtype: str
        """
        return self._wildcard_policy

    @wildcard_policy.setter
    def wildcard_policy(self, wildcard_policy):
        """
        Sets the wildcard_policy of this V1RouteIngress.
        Wildcard policy is the wildcard policy that was allowed where this route is exposed.

        :param wildcard_policy: The wildcard_policy of this V1RouteIngress.
        :type: str
        """

        self._wildcard_policy = wildcard_policy

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
        if not isinstance(other, V1RouteIngress):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
