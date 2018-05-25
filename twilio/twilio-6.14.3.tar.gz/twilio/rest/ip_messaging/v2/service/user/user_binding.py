# coding=utf-8
"""
This code was generated by
\ / _    _  _|   _  _
 | (_)\/(_)(_|\/| |(/_  v1.0.0
      /       /
"""

from twilio.base import deserialize
from twilio.base import serialize
from twilio.base import values
from twilio.base.instance_context import InstanceContext
from twilio.base.instance_resource import InstanceResource
from twilio.base.list_resource import ListResource
from twilio.base.page import Page


class UserBindingList(ListResource):
    """  """

    def __init__(self, version, service_sid, user_sid):
        """
        Initialize the UserBindingList

        :param Version version: Version that contains the resource
        :param service_sid: The unique id of the Service this binding belongs to.
        :param user_sid: The unique id of the User for this binding.

        :returns: twilio.rest.chat.v2.service.user.user_binding.UserBindingList
        :rtype: twilio.rest.chat.v2.service.user.user_binding.UserBindingList
        """
        super(UserBindingList, self).__init__(version)

        # Path Solution
        self._solution = {'service_sid': service_sid, 'user_sid': user_sid, }
        self._uri = '/Services/{service_sid}/Users/{user_sid}/Bindings'.format(**self._solution)

    def stream(self, binding_type=values.unset, limit=None, page_size=None):
        """
        Streams UserBindingInstance records from the API as a generator stream.
        This operation lazily loads records as efficiently as possible until the limit
        is reached.
        The results are returned as a generator, so this operation is memory efficient.

        :param UserBindingInstance.BindingType binding_type: The push technology used for the bindings returned.
        :param int limit: Upper limit for the number of records to return. stream()
                          guarantees to never return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, stream() will attempt to read the
                              limit with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.chat.v2.service.user.user_binding.UserBindingInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(binding_type=binding_type, page_size=limits['page_size'], )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, binding_type=values.unset, limit=None, page_size=None):
        """
        Lists UserBindingInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param UserBindingInstance.BindingType binding_type: The push technology used for the bindings returned.
        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.chat.v2.service.user.user_binding.UserBindingInstance]
        """
        return list(self.stream(binding_type=binding_type, limit=limit, page_size=page_size, ))

    def page(self, binding_type=values.unset, page_token=values.unset,
             page_number=values.unset, page_size=values.unset):
        """
        Retrieve a single page of UserBindingInstance records from the API.
        Request is executed immediately

        :param UserBindingInstance.BindingType binding_type: The push technology used for the bindings returned.
        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of UserBindingInstance
        :rtype: twilio.rest.chat.v2.service.user.user_binding.UserBindingPage
        """
        params = values.of({
            'BindingType': serialize.map(binding_type, lambda e: e),
            'PageToken': page_token,
            'Page': page_number,
            'PageSize': page_size,
        })

        response = self._version.page(
            'GET',
            self._uri,
            params=params,
        )

        return UserBindingPage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of UserBindingInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of UserBindingInstance
        :rtype: twilio.rest.chat.v2.service.user.user_binding.UserBindingPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return UserBindingPage(self._version, response, self._solution)

    def get(self, sid):
        """
        Constructs a UserBindingContext

        :param sid: The sid

        :returns: twilio.rest.chat.v2.service.user.user_binding.UserBindingContext
        :rtype: twilio.rest.chat.v2.service.user.user_binding.UserBindingContext
        """
        return UserBindingContext(
            self._version,
            service_sid=self._solution['service_sid'],
            user_sid=self._solution['user_sid'],
            sid=sid,
        )

    def __call__(self, sid):
        """
        Constructs a UserBindingContext

        :param sid: The sid

        :returns: twilio.rest.chat.v2.service.user.user_binding.UserBindingContext
        :rtype: twilio.rest.chat.v2.service.user.user_binding.UserBindingContext
        """
        return UserBindingContext(
            self._version,
            service_sid=self._solution['service_sid'],
            user_sid=self._solution['user_sid'],
            sid=sid,
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.IpMessaging.V2.UserBindingList>'


class UserBindingPage(Page):
    """  """

    def __init__(self, version, response, solution):
        """
        Initialize the UserBindingPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API
        :param service_sid: The unique id of the Service this binding belongs to.
        :param user_sid: The unique id of the User for this binding.

        :returns: twilio.rest.chat.v2.service.user.user_binding.UserBindingPage
        :rtype: twilio.rest.chat.v2.service.user.user_binding.UserBindingPage
        """
        super(UserBindingPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of UserBindingInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.chat.v2.service.user.user_binding.UserBindingInstance
        :rtype: twilio.rest.chat.v2.service.user.user_binding.UserBindingInstance
        """
        return UserBindingInstance(
            self._version,
            payload,
            service_sid=self._solution['service_sid'],
            user_sid=self._solution['user_sid'],
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.IpMessaging.V2.UserBindingPage>'


class UserBindingContext(InstanceContext):
    """  """

    def __init__(self, version, service_sid, user_sid, sid):
        """
        Initialize the UserBindingContext

        :param Version version: Version that contains the resource
        :param service_sid: The service_sid
        :param user_sid: The user_sid
        :param sid: The sid

        :returns: twilio.rest.chat.v2.service.user.user_binding.UserBindingContext
        :rtype: twilio.rest.chat.v2.service.user.user_binding.UserBindingContext
        """
        super(UserBindingContext, self).__init__(version)

        # Path Solution
        self._solution = {'service_sid': service_sid, 'user_sid': user_sid, 'sid': sid, }
        self._uri = '/Services/{service_sid}/Users/{user_sid}/Bindings/{sid}'.format(**self._solution)

    def fetch(self):
        """
        Fetch a UserBindingInstance

        :returns: Fetched UserBindingInstance
        :rtype: twilio.rest.chat.v2.service.user.user_binding.UserBindingInstance
        """
        params = values.of({})

        payload = self._version.fetch(
            'GET',
            self._uri,
            params=params,
        )

        return UserBindingInstance(
            self._version,
            payload,
            service_sid=self._solution['service_sid'],
            user_sid=self._solution['user_sid'],
            sid=self._solution['sid'],
        )

    def delete(self):
        """
        Deletes the UserBindingInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._version.delete('delete', self._uri)

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.IpMessaging.V2.UserBindingContext {}>'.format(context)


class UserBindingInstance(InstanceResource):
    """  """

    class BindingType(object):
        GCM = "gcm"
        APN = "apn"
        FCM = "fcm"

    def __init__(self, version, payload, service_sid, user_sid, sid=None):
        """
        Initialize the UserBindingInstance

        :returns: twilio.rest.chat.v2.service.user.user_binding.UserBindingInstance
        :rtype: twilio.rest.chat.v2.service.user.user_binding.UserBindingInstance
        """
        super(UserBindingInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'sid': payload['sid'],
            'account_sid': payload['account_sid'],
            'service_sid': payload['service_sid'],
            'date_created': deserialize.iso8601_datetime(payload['date_created']),
            'date_updated': deserialize.iso8601_datetime(payload['date_updated']),
            'endpoint': payload['endpoint'],
            'identity': payload['identity'],
            'user_sid': payload['user_sid'],
            'credential_sid': payload['credential_sid'],
            'binding_type': payload['binding_type'],
            'message_types': payload['message_types'],
            'url': payload['url'],
        }

        # Context
        self._context = None
        self._solution = {
            'service_sid': service_sid,
            'user_sid': user_sid,
            'sid': sid or self._properties['sid'],
        }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: UserBindingContext for this UserBindingInstance
        :rtype: twilio.rest.chat.v2.service.user.user_binding.UserBindingContext
        """
        if self._context is None:
            self._context = UserBindingContext(
                self._version,
                service_sid=self._solution['service_sid'],
                user_sid=self._solution['user_sid'],
                sid=self._solution['sid'],
            )
        return self._context

    @property
    def sid(self):
        """
        :returns: A 34 character string that uniquely identifies this resource.
        :rtype: unicode
        """
        return self._properties['sid']

    @property
    def account_sid(self):
        """
        :returns: The unique id of the Account responsible for this binding.
        :rtype: unicode
        """
        return self._properties['account_sid']

    @property
    def service_sid(self):
        """
        :returns: The unique id of the Service this binding belongs to.
        :rtype: unicode
        """
        return self._properties['service_sid']

    @property
    def date_created(self):
        """
        :returns: The date that this resource was created.
        :rtype: datetime
        """
        return self._properties['date_created']

    @property
    def date_updated(self):
        """
        :returns: The date that this resource was last updated.
        :rtype: datetime
        """
        return self._properties['date_updated']

    @property
    def endpoint(self):
        """
        :returns: The unique endpoint identifier for this Binding.
        :rtype: unicode
        """
        return self._properties['endpoint']

    @property
    def identity(self):
        """
        :returns: A unique string identifier for the Binding for this User in this Service.
        :rtype: unicode
        """
        return self._properties['identity']

    @property
    def user_sid(self):
        """
        :returns: The unique id of the User for this binding.
        :rtype: unicode
        """
        return self._properties['user_sid']

    @property
    def credential_sid(self):
        """
        :returns: The unique id of the Credential for this binding.
        :rtype: unicode
        """
        return self._properties['credential_sid']

    @property
    def binding_type(self):
        """
        :returns: The push technology to use for this binding.
        :rtype: UserBindingInstance.BindingType
        """
        return self._properties['binding_type']

    @property
    def message_types(self):
        """
        :returns: List of message types for this binding.
        :rtype: unicode
        """
        return self._properties['message_types']

    @property
    def url(self):
        """
        :returns: An absolute URL for this binding.
        :rtype: unicode
        """
        return self._properties['url']

    def fetch(self):
        """
        Fetch a UserBindingInstance

        :returns: Fetched UserBindingInstance
        :rtype: twilio.rest.chat.v2.service.user.user_binding.UserBindingInstance
        """
        return self._proxy.fetch()

    def delete(self):
        """
        Deletes the UserBindingInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._proxy.delete()

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.IpMessaging.V2.UserBindingInstance {}>'.format(context)
