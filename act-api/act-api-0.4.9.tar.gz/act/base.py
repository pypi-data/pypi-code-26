import json
from logging import error
import requests
from .schema import Schema, Field, schema_doc


class NotImplemented(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class ArgumentError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class ResponseError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def request(method, user_id, url, **kwargs):
    """Perform requests towards API

Args:
    method (str):         POST|GET
    user_id (int):        Act user ID
    url (str):            Absolute URL for the endpoint
    **kwargs (keywords):  Additional options passed to requests json parameter
                          the following fields:
"""

    res = requests.request(
        method,
        url,
        headers={
            "ACT-User-ID": str(user_id)
        },
        **kwargs
    )

    if res.status_code == 412:
        error("Request failed: {}, {}, {}".format(
            url, kwargs, res.status_code))
        raise ResponseError(res.text)

    elif res.status_code not in (200, 201):
        error("Request failed: {}, {}, {}".format(
            url, kwargs, res.status_code))
        raise ResponseError(
            "Unknown response error {}: {}".format(res.status_code, res.text))

    try:
        return res.json()

    except json.decoder.JSONDecodeError:
        raise ResponseError(
            "Error decoding response {}: {}".format(res.status_code, res.text))


class ActResultSet(object):
    """Represents a list of Act entries"""

    def __init__(self, response, deserializer):
        """Initialize result set
Args:
    response (str):       JSON response from Act. This should include
                          the following fields:
                            - count: the number of entries fetched
                            - limit: the limit in the query
                            - responseCode: responseCode from the API
                            - size: the total number of entries in the platform
                            - data (array): array of entries

    deserializer (class): Deseralizer class
"""

        if not isinstance(response["data"], list):
            raise ResponseError(
                "Response should be list: {}".format(
                    response["data"]))

        self.data = [deserializer(**d) for d in response["data"]]

        self.size = response["size"]
        self.count = response["count"]
        self.limit = response["limit"]
        self.status_code = response["responseCode"]

    @property
    def complete(self):
        """Returns true if we have recieved all data that exists on the endpoint"""
        return self.size >= self.count

    def __call__(self, func, *args, **kwargs):
        """Call function on each data entry"""

        self.data = [getattr(item, func)(*args, **kwargs)
                     for item in self.data]
        return self

    def __len__(self):
        """Returns the number of entries"""
        return len(self.data)

    def __repr__(self):
        return str(self.data)

    def __getitem__(self, sliced):
        return self.data[sliced]

    def __iter__(self):
        """Iterate over the entries"""
        return self.data.__iter__()


class ActBase(Schema):
    """Act object inheriting Schema, to support serializing and
    deserializing."""

    act_baseurl = None
    user_id = None

    SCHEMA = []

    @schema_doc(SCHEMA)
    def __init__(self, *args, **kwargs):
        super(ActBase, self).__init__(*args, **kwargs)

    def auth(self, act_baseurl, user_id):
        """Set URL and USER ID used to connect to the API"""

        self.act_baseurl = act_baseurl
        self.user_id = user_id
        return self

    def api_request(self, method, uri, **kwargs):
        """Send request to API and update current object with result"""

        response = request(
            method,
            self.user_id,
            "{}/{}".format(self.act_baseurl, uri),
            **kwargs
        )

        return response

    def api_post(self, uri, **kwargs):
        """Send POST request to API with keywords as JSON arguments"""

        return self.api_request("POST", uri, json=kwargs)

    def api_put(self, uri, **kwargs):
        """Send PUT request to API with keywords as JSON arguments"""

        return self.api_request("PUT", uri, json=kwargs)

    def api_get(self, uri):
        """Send GET request to API"""

        return self.api_request("GET", uri)


class NameSpace(ActBase):
    """Namespace - serialized object specifying Namespace"""

    SCHEMA = [
        Field("name"),
        Field("id"),
    ]


class Organization(ActBase):
    """Manage FactSource"""

    SCHEMA = [
        Field("name"),
        Field("id"),
    ]


class Source(ActBase):
    """Manage FactSource"""

    SCHEMA = [
        Field("name"),
        Field("id"),
    ]


class Comment(ActBase):
    """Namespace - serialized object specifying Namespace"""

    SCHEMA = [
        Field("comment"),
        Field("id"),
        Field("timestamp", serializer=False),
        Field("reply_to"),
        Field("source", deserializer=Source, serializer=False),
    ]
