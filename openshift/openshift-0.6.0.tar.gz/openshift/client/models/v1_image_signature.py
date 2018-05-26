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


class V1ImageSignature(object):
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
        'api_version': 'str',
        'conditions': 'list[V1SignatureCondition]',
        'content': 'str',
        'created': 'datetime',
        'image_identity': 'str',
        'issued_by': 'V1SignatureIssuer',
        'issued_to': 'V1SignatureSubject',
        'kind': 'str',
        'metadata': 'V1ObjectMeta',
        'signed_claims': 'dict(str, str)',
        'type': 'str'
    }

    attribute_map = {
        'api_version': 'apiVersion',
        'conditions': 'conditions',
        'content': 'content',
        'created': 'created',
        'image_identity': 'imageIdentity',
        'issued_by': 'issuedBy',
        'issued_to': 'issuedTo',
        'kind': 'kind',
        'metadata': 'metadata',
        'signed_claims': 'signedClaims',
        'type': 'type'
    }

    def __init__(self, api_version=None, conditions=None, content=None, created=None, image_identity=None, issued_by=None, issued_to=None, kind=None, metadata=None, signed_claims=None, type=None):
        """
        V1ImageSignature - a model defined in Swagger
        """

        self._api_version = None
        self._conditions = None
        self._content = None
        self._created = None
        self._image_identity = None
        self._issued_by = None
        self._issued_to = None
        self._kind = None
        self._metadata = None
        self._signed_claims = None
        self._type = None
        self.discriminator = None

        if api_version is not None:
          self.api_version = api_version
        if conditions is not None:
          self.conditions = conditions
        self.content = content
        if created is not None:
          self.created = created
        if image_identity is not None:
          self.image_identity = image_identity
        if issued_by is not None:
          self.issued_by = issued_by
        if issued_to is not None:
          self.issued_to = issued_to
        if kind is not None:
          self.kind = kind
        if metadata is not None:
          self.metadata = metadata
        if signed_claims is not None:
          self.signed_claims = signed_claims
        self.type = type

    @property
    def api_version(self):
        """
        Gets the api_version of this V1ImageSignature.
        APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#resources

        :return: The api_version of this V1ImageSignature.
        :rtype: str
        """
        return self._api_version

    @api_version.setter
    def api_version(self, api_version):
        """
        Sets the api_version of this V1ImageSignature.
        APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#resources

        :param api_version: The api_version of this V1ImageSignature.
        :type: str
        """

        self._api_version = api_version

    @property
    def conditions(self):
        """
        Gets the conditions of this V1ImageSignature.
        Conditions represent the latest available observations of a signature's current state.

        :return: The conditions of this V1ImageSignature.
        :rtype: list[V1SignatureCondition]
        """
        return self._conditions

    @conditions.setter
    def conditions(self, conditions):
        """
        Sets the conditions of this V1ImageSignature.
        Conditions represent the latest available observations of a signature's current state.

        :param conditions: The conditions of this V1ImageSignature.
        :type: list[V1SignatureCondition]
        """

        self._conditions = conditions

    @property
    def content(self):
        """
        Gets the content of this V1ImageSignature.
        Required: An opaque binary string which is an image's signature.

        :return: The content of this V1ImageSignature.
        :rtype: str
        """
        return self._content

    @content.setter
    def content(self, content):
        """
        Sets the content of this V1ImageSignature.
        Required: An opaque binary string which is an image's signature.

        :param content: The content of this V1ImageSignature.
        :type: str
        """
        if content is None:
            raise ValueError("Invalid value for `content`, must not be `None`")
        if content is not None and not re.search('^(?:[A-Za-z0-9+\/]{4})*(?:[A-Za-z0-9+\/]{2}==|[A-Za-z0-9+\/]{3}=)?$', content):
            raise ValueError("Invalid value for `content`, must be a follow pattern or equal to `/^(?:[A-Za-z0-9+\/]{4})*(?:[A-Za-z0-9+\/]{2}==|[A-Za-z0-9+\/]{3}=)?$/`")

        self._content = content

    @property
    def created(self):
        """
        Gets the created of this V1ImageSignature.
        If specified, it is the time of signature's creation.

        :return: The created of this V1ImageSignature.
        :rtype: datetime
        """
        return self._created

    @created.setter
    def created(self, created):
        """
        Sets the created of this V1ImageSignature.
        If specified, it is the time of signature's creation.

        :param created: The created of this V1ImageSignature.
        :type: datetime
        """

        self._created = created

    @property
    def image_identity(self):
        """
        Gets the image_identity of this V1ImageSignature.
        A human readable string representing image's identity. It could be a product name and version, or an image pull spec (e.g. \"registry.access.redhat.com/rhel7/rhel:7.2\").

        :return: The image_identity of this V1ImageSignature.
        :rtype: str
        """
        return self._image_identity

    @image_identity.setter
    def image_identity(self, image_identity):
        """
        Sets the image_identity of this V1ImageSignature.
        A human readable string representing image's identity. It could be a product name and version, or an image pull spec (e.g. \"registry.access.redhat.com/rhel7/rhel:7.2\").

        :param image_identity: The image_identity of this V1ImageSignature.
        :type: str
        """

        self._image_identity = image_identity

    @property
    def issued_by(self):
        """
        Gets the issued_by of this V1ImageSignature.
        If specified, it holds information about an issuer of signing certificate or key (a person or entity who signed the signing certificate or key).

        :return: The issued_by of this V1ImageSignature.
        :rtype: V1SignatureIssuer
        """
        return self._issued_by

    @issued_by.setter
    def issued_by(self, issued_by):
        """
        Sets the issued_by of this V1ImageSignature.
        If specified, it holds information about an issuer of signing certificate or key (a person or entity who signed the signing certificate or key).

        :param issued_by: The issued_by of this V1ImageSignature.
        :type: V1SignatureIssuer
        """

        self._issued_by = issued_by

    @property
    def issued_to(self):
        """
        Gets the issued_to of this V1ImageSignature.
        If specified, it holds information about a subject of signing certificate or key (a person or entity who signed the image).

        :return: The issued_to of this V1ImageSignature.
        :rtype: V1SignatureSubject
        """
        return self._issued_to

    @issued_to.setter
    def issued_to(self, issued_to):
        """
        Sets the issued_to of this V1ImageSignature.
        If specified, it holds information about a subject of signing certificate or key (a person or entity who signed the image).

        :param issued_to: The issued_to of this V1ImageSignature.
        :type: V1SignatureSubject
        """

        self._issued_to = issued_to

    @property
    def kind(self):
        """
        Gets the kind of this V1ImageSignature.
        Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#types-kinds

        :return: The kind of this V1ImageSignature.
        :rtype: str
        """
        return self._kind

    @kind.setter
    def kind(self, kind):
        """
        Sets the kind of this V1ImageSignature.
        Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#types-kinds

        :param kind: The kind of this V1ImageSignature.
        :type: str
        """

        self._kind = kind

    @property
    def metadata(self):
        """
        Gets the metadata of this V1ImageSignature.
        Standard object's metadata.

        :return: The metadata of this V1ImageSignature.
        :rtype: V1ObjectMeta
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """
        Sets the metadata of this V1ImageSignature.
        Standard object's metadata.

        :param metadata: The metadata of this V1ImageSignature.
        :type: V1ObjectMeta
        """

        self._metadata = metadata

    @property
    def signed_claims(self):
        """
        Gets the signed_claims of this V1ImageSignature.
        Contains claims from the signature.

        :return: The signed_claims of this V1ImageSignature.
        :rtype: dict(str, str)
        """
        return self._signed_claims

    @signed_claims.setter
    def signed_claims(self, signed_claims):
        """
        Sets the signed_claims of this V1ImageSignature.
        Contains claims from the signature.

        :param signed_claims: The signed_claims of this V1ImageSignature.
        :type: dict(str, str)
        """

        self._signed_claims = signed_claims

    @property
    def type(self):
        """
        Gets the type of this V1ImageSignature.
        Required: Describes a type of stored blob.

        :return: The type of this V1ImageSignature.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """
        Sets the type of this V1ImageSignature.
        Required: Describes a type of stored blob.

        :param type: The type of this V1ImageSignature.
        :type: str
        """
        if type is None:
            raise ValueError("Invalid value for `type`, must not be `None`")

        self._type = type

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
        if not isinstance(other, V1ImageSignature):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
