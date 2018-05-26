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


class V1OAuthAccessToken(object):
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
        'authorize_token': 'str',
        'client_name': 'str',
        'expires_in': 'int',
        'inactivity_timeout_seconds': 'int',
        'kind': 'str',
        'metadata': 'V1ObjectMeta',
        'redirect_uri': 'str',
        'refresh_token': 'str',
        'scopes': 'list[str]',
        'user_name': 'str',
        'user_uid': 'str'
    }

    attribute_map = {
        'api_version': 'apiVersion',
        'authorize_token': 'authorizeToken',
        'client_name': 'clientName',
        'expires_in': 'expiresIn',
        'inactivity_timeout_seconds': 'inactivityTimeoutSeconds',
        'kind': 'kind',
        'metadata': 'metadata',
        'redirect_uri': 'redirectURI',
        'refresh_token': 'refreshToken',
        'scopes': 'scopes',
        'user_name': 'userName',
        'user_uid': 'userUID'
    }

    def __init__(self, api_version=None, authorize_token=None, client_name=None, expires_in=None, inactivity_timeout_seconds=None, kind=None, metadata=None, redirect_uri=None, refresh_token=None, scopes=None, user_name=None, user_uid=None):
        """
        V1OAuthAccessToken - a model defined in Swagger
        """

        self._api_version = None
        self._authorize_token = None
        self._client_name = None
        self._expires_in = None
        self._inactivity_timeout_seconds = None
        self._kind = None
        self._metadata = None
        self._redirect_uri = None
        self._refresh_token = None
        self._scopes = None
        self._user_name = None
        self._user_uid = None
        self.discriminator = None

        if api_version is not None:
          self.api_version = api_version
        if authorize_token is not None:
          self.authorize_token = authorize_token
        if client_name is not None:
          self.client_name = client_name
        if expires_in is not None:
          self.expires_in = expires_in
        if inactivity_timeout_seconds is not None:
          self.inactivity_timeout_seconds = inactivity_timeout_seconds
        if kind is not None:
          self.kind = kind
        if metadata is not None:
          self.metadata = metadata
        if redirect_uri is not None:
          self.redirect_uri = redirect_uri
        if refresh_token is not None:
          self.refresh_token = refresh_token
        if scopes is not None:
          self.scopes = scopes
        if user_name is not None:
          self.user_name = user_name
        if user_uid is not None:
          self.user_uid = user_uid

    @property
    def api_version(self):
        """
        Gets the api_version of this V1OAuthAccessToken.
        APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#resources

        :return: The api_version of this V1OAuthAccessToken.
        :rtype: str
        """
        return self._api_version

    @api_version.setter
    def api_version(self, api_version):
        """
        Sets the api_version of this V1OAuthAccessToken.
        APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#resources

        :param api_version: The api_version of this V1OAuthAccessToken.
        :type: str
        """

        self._api_version = api_version

    @property
    def authorize_token(self):
        """
        Gets the authorize_token of this V1OAuthAccessToken.
        AuthorizeToken contains the token that authorized this token

        :return: The authorize_token of this V1OAuthAccessToken.
        :rtype: str
        """
        return self._authorize_token

    @authorize_token.setter
    def authorize_token(self, authorize_token):
        """
        Sets the authorize_token of this V1OAuthAccessToken.
        AuthorizeToken contains the token that authorized this token

        :param authorize_token: The authorize_token of this V1OAuthAccessToken.
        :type: str
        """

        self._authorize_token = authorize_token

    @property
    def client_name(self):
        """
        Gets the client_name of this V1OAuthAccessToken.
        ClientName references the client that created this token.

        :return: The client_name of this V1OAuthAccessToken.
        :rtype: str
        """
        return self._client_name

    @client_name.setter
    def client_name(self, client_name):
        """
        Sets the client_name of this V1OAuthAccessToken.
        ClientName references the client that created this token.

        :param client_name: The client_name of this V1OAuthAccessToken.
        :type: str
        """

        self._client_name = client_name

    @property
    def expires_in(self):
        """
        Gets the expires_in of this V1OAuthAccessToken.
        ExpiresIn is the seconds from CreationTime before this token expires.

        :return: The expires_in of this V1OAuthAccessToken.
        :rtype: int
        """
        return self._expires_in

    @expires_in.setter
    def expires_in(self, expires_in):
        """
        Sets the expires_in of this V1OAuthAccessToken.
        ExpiresIn is the seconds from CreationTime before this token expires.

        :param expires_in: The expires_in of this V1OAuthAccessToken.
        :type: int
        """

        self._expires_in = expires_in

    @property
    def inactivity_timeout_seconds(self):
        """
        Gets the inactivity_timeout_seconds of this V1OAuthAccessToken.
        InactivityTimeoutSeconds is the value in seconds, from the CreationTimestamp, after which this token can no longer be used. The value is automatically incremented when the token is used.

        :return: The inactivity_timeout_seconds of this V1OAuthAccessToken.
        :rtype: int
        """
        return self._inactivity_timeout_seconds

    @inactivity_timeout_seconds.setter
    def inactivity_timeout_seconds(self, inactivity_timeout_seconds):
        """
        Sets the inactivity_timeout_seconds of this V1OAuthAccessToken.
        InactivityTimeoutSeconds is the value in seconds, from the CreationTimestamp, after which this token can no longer be used. The value is automatically incremented when the token is used.

        :param inactivity_timeout_seconds: The inactivity_timeout_seconds of this V1OAuthAccessToken.
        :type: int
        """

        self._inactivity_timeout_seconds = inactivity_timeout_seconds

    @property
    def kind(self):
        """
        Gets the kind of this V1OAuthAccessToken.
        Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#types-kinds

        :return: The kind of this V1OAuthAccessToken.
        :rtype: str
        """
        return self._kind

    @kind.setter
    def kind(self, kind):
        """
        Sets the kind of this V1OAuthAccessToken.
        Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#types-kinds

        :param kind: The kind of this V1OAuthAccessToken.
        :type: str
        """

        self._kind = kind

    @property
    def metadata(self):
        """
        Gets the metadata of this V1OAuthAccessToken.
        Standard object's metadata.

        :return: The metadata of this V1OAuthAccessToken.
        :rtype: V1ObjectMeta
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """
        Sets the metadata of this V1OAuthAccessToken.
        Standard object's metadata.

        :param metadata: The metadata of this V1OAuthAccessToken.
        :type: V1ObjectMeta
        """

        self._metadata = metadata

    @property
    def redirect_uri(self):
        """
        Gets the redirect_uri of this V1OAuthAccessToken.
        RedirectURI is the redirection associated with the token.

        :return: The redirect_uri of this V1OAuthAccessToken.
        :rtype: str
        """
        return self._redirect_uri

    @redirect_uri.setter
    def redirect_uri(self, redirect_uri):
        """
        Sets the redirect_uri of this V1OAuthAccessToken.
        RedirectURI is the redirection associated with the token.

        :param redirect_uri: The redirect_uri of this V1OAuthAccessToken.
        :type: str
        """

        self._redirect_uri = redirect_uri

    @property
    def refresh_token(self):
        """
        Gets the refresh_token of this V1OAuthAccessToken.
        RefreshToken is the value by which this token can be renewed. Can be blank.

        :return: The refresh_token of this V1OAuthAccessToken.
        :rtype: str
        """
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, refresh_token):
        """
        Sets the refresh_token of this V1OAuthAccessToken.
        RefreshToken is the value by which this token can be renewed. Can be blank.

        :param refresh_token: The refresh_token of this V1OAuthAccessToken.
        :type: str
        """

        self._refresh_token = refresh_token

    @property
    def scopes(self):
        """
        Gets the scopes of this V1OAuthAccessToken.
        Scopes is an array of the requested scopes.

        :return: The scopes of this V1OAuthAccessToken.
        :rtype: list[str]
        """
        return self._scopes

    @scopes.setter
    def scopes(self, scopes):
        """
        Sets the scopes of this V1OAuthAccessToken.
        Scopes is an array of the requested scopes.

        :param scopes: The scopes of this V1OAuthAccessToken.
        :type: list[str]
        """

        self._scopes = scopes

    @property
    def user_name(self):
        """
        Gets the user_name of this V1OAuthAccessToken.
        UserName is the user name associated with this token

        :return: The user_name of this V1OAuthAccessToken.
        :rtype: str
        """
        return self._user_name

    @user_name.setter
    def user_name(self, user_name):
        """
        Sets the user_name of this V1OAuthAccessToken.
        UserName is the user name associated with this token

        :param user_name: The user_name of this V1OAuthAccessToken.
        :type: str
        """

        self._user_name = user_name

    @property
    def user_uid(self):
        """
        Gets the user_uid of this V1OAuthAccessToken.
        UserUID is the unique UID associated with this token

        :return: The user_uid of this V1OAuthAccessToken.
        :rtype: str
        """
        return self._user_uid

    @user_uid.setter
    def user_uid(self, user_uid):
        """
        Sets the user_uid of this V1OAuthAccessToken.
        UserUID is the unique UID associated with this token

        :param user_uid: The user_uid of this V1OAuthAccessToken.
        :type: str
        """

        self._user_uid = user_uid

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
        if not isinstance(other, V1OAuthAccessToken):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
