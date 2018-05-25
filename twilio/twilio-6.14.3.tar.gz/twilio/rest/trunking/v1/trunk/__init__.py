# coding=utf-8
"""
This code was generated by
\ / _    _  _|   _  _
 | (_)\/(_)(_|\/| |(/_  v1.0.0
      /       /
"""

from twilio.base import deserialize
from twilio.base import values
from twilio.base.instance_context import InstanceContext
from twilio.base.instance_resource import InstanceResource
from twilio.base.list_resource import ListResource
from twilio.base.page import Page
from twilio.rest.trunking.v1.trunk.credential_list import CredentialListList
from twilio.rest.trunking.v1.trunk.ip_access_control_list import IpAccessControlListList
from twilio.rest.trunking.v1.trunk.origination_url import OriginationUrlList
from twilio.rest.trunking.v1.trunk.phone_number import PhoneNumberList


class TrunkList(ListResource):
    """  """

    def __init__(self, version):
        """
        Initialize the TrunkList

        :param Version version: Version that contains the resource

        :returns: twilio.rest.trunking.v1.trunk.TrunkList
        :rtype: twilio.rest.trunking.v1.trunk.TrunkList
        """
        super(TrunkList, self).__init__(version)

        # Path Solution
        self._solution = {}
        self._uri = '/Trunks'.format(**self._solution)

    def create(self, friendly_name=values.unset, domain_name=values.unset,
               disaster_recovery_url=values.unset,
               disaster_recovery_method=values.unset, recording=values.unset,
               secure=values.unset, cnam_lookup_enabled=values.unset):
        """
        Create a new TrunkInstance

        :param unicode friendly_name: A human-readable name for the Trunk.
        :param unicode domain_name: The unique address you reserve on Twilio to which you route your SIP traffic.
        :param unicode disaster_recovery_url: The HTTP URL that Twilio will request if an error occurs while sending SIP traffic towards your configured Origination URL.
        :param unicode disaster_recovery_method: The HTTP method Twilio will use when requesting the DisasterRecoveryUrl.
        :param TrunkInstance.RecordingSetting recording: The recording settings for this trunk.
        :param bool secure: The Secure Trunking  settings for this trunk.
        :param bool cnam_lookup_enabled: The cnam_lookup_enabled

        :returns: Newly created TrunkInstance
        :rtype: twilio.rest.trunking.v1.trunk.TrunkInstance
        """
        data = values.of({
            'FriendlyName': friendly_name,
            'DomainName': domain_name,
            'DisasterRecoveryUrl': disaster_recovery_url,
            'DisasterRecoveryMethod': disaster_recovery_method,
            'Recording': recording,
            'Secure': secure,
            'CnamLookupEnabled': cnam_lookup_enabled,
        })

        payload = self._version.create(
            'POST',
            self._uri,
            data=data,
        )

        return TrunkInstance(self._version, payload, )

    def stream(self, limit=None, page_size=None):
        """
        Streams TrunkInstance records from the API as a generator stream.
        This operation lazily loads records as efficiently as possible until the limit
        is reached.
        The results are returned as a generator, so this operation is memory efficient.

        :param int limit: Upper limit for the number of records to return. stream()
                          guarantees to never return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, stream() will attempt to read the
                              limit with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.trunking.v1.trunk.TrunkInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(page_size=limits['page_size'], )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, limit=None, page_size=None):
        """
        Lists TrunkInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.trunking.v1.trunk.TrunkInstance]
        """
        return list(self.stream(limit=limit, page_size=page_size, ))

    def page(self, page_token=values.unset, page_number=values.unset,
             page_size=values.unset):
        """
        Retrieve a single page of TrunkInstance records from the API.
        Request is executed immediately

        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of TrunkInstance
        :rtype: twilio.rest.trunking.v1.trunk.TrunkPage
        """
        params = values.of({'PageToken': page_token, 'Page': page_number, 'PageSize': page_size, })

        response = self._version.page(
            'GET',
            self._uri,
            params=params,
        )

        return TrunkPage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of TrunkInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of TrunkInstance
        :rtype: twilio.rest.trunking.v1.trunk.TrunkPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return TrunkPage(self._version, response, self._solution)

    def get(self, sid):
        """
        Constructs a TrunkContext

        :param sid: The sid

        :returns: twilio.rest.trunking.v1.trunk.TrunkContext
        :rtype: twilio.rest.trunking.v1.trunk.TrunkContext
        """
        return TrunkContext(self._version, sid=sid, )

    def __call__(self, sid):
        """
        Constructs a TrunkContext

        :param sid: The sid

        :returns: twilio.rest.trunking.v1.trunk.TrunkContext
        :rtype: twilio.rest.trunking.v1.trunk.TrunkContext
        """
        return TrunkContext(self._version, sid=sid, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Trunking.V1.TrunkList>'


class TrunkPage(Page):
    """  """

    def __init__(self, version, response, solution):
        """
        Initialize the TrunkPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API

        :returns: twilio.rest.trunking.v1.trunk.TrunkPage
        :rtype: twilio.rest.trunking.v1.trunk.TrunkPage
        """
        super(TrunkPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of TrunkInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.trunking.v1.trunk.TrunkInstance
        :rtype: twilio.rest.trunking.v1.trunk.TrunkInstance
        """
        return TrunkInstance(self._version, payload, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Trunking.V1.TrunkPage>'


class TrunkContext(InstanceContext):
    """  """

    def __init__(self, version, sid):
        """
        Initialize the TrunkContext

        :param Version version: Version that contains the resource
        :param sid: The sid

        :returns: twilio.rest.trunking.v1.trunk.TrunkContext
        :rtype: twilio.rest.trunking.v1.trunk.TrunkContext
        """
        super(TrunkContext, self).__init__(version)

        # Path Solution
        self._solution = {'sid': sid, }
        self._uri = '/Trunks/{sid}'.format(**self._solution)

        # Dependents
        self._origination_urls = None
        self._credentials_lists = None
        self._ip_access_control_lists = None
        self._phone_numbers = None

    def fetch(self):
        """
        Fetch a TrunkInstance

        :returns: Fetched TrunkInstance
        :rtype: twilio.rest.trunking.v1.trunk.TrunkInstance
        """
        params = values.of({})

        payload = self._version.fetch(
            'GET',
            self._uri,
            params=params,
        )

        return TrunkInstance(self._version, payload, sid=self._solution['sid'], )

    def delete(self):
        """
        Deletes the TrunkInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._version.delete('delete', self._uri)

    def update(self, friendly_name=values.unset, domain_name=values.unset,
               disaster_recovery_url=values.unset,
               disaster_recovery_method=values.unset, recording=values.unset,
               secure=values.unset, cnam_lookup_enabled=values.unset):
        """
        Update the TrunkInstance

        :param unicode friendly_name: A human-readable name for the Trunk.
        :param unicode domain_name: The unique address you reserve on Twilio to which you route your SIP traffic.
        :param unicode disaster_recovery_url: The HTTP URL that Twilio will request if an error occurs while sending SIP traffic towards your configured Origination URL.
        :param unicode disaster_recovery_method: The HTTP method Twilio will use when requesting the DisasterRecoveryUrl.
        :param TrunkInstance.RecordingSetting recording: The recording settings for this trunk.
        :param bool secure: The Secure Trunking  settings for this trunk.
        :param bool cnam_lookup_enabled: The cnam_lookup_enabled

        :returns: Updated TrunkInstance
        :rtype: twilio.rest.trunking.v1.trunk.TrunkInstance
        """
        data = values.of({
            'FriendlyName': friendly_name,
            'DomainName': domain_name,
            'DisasterRecoveryUrl': disaster_recovery_url,
            'DisasterRecoveryMethod': disaster_recovery_method,
            'Recording': recording,
            'Secure': secure,
            'CnamLookupEnabled': cnam_lookup_enabled,
        })

        payload = self._version.update(
            'POST',
            self._uri,
            data=data,
        )

        return TrunkInstance(self._version, payload, sid=self._solution['sid'], )

    @property
    def origination_urls(self):
        """
        Access the origination_urls

        :returns: twilio.rest.trunking.v1.trunk.origination_url.OriginationUrlList
        :rtype: twilio.rest.trunking.v1.trunk.origination_url.OriginationUrlList
        """
        if self._origination_urls is None:
            self._origination_urls = OriginationUrlList(self._version, trunk_sid=self._solution['sid'], )
        return self._origination_urls

    @property
    def credentials_lists(self):
        """
        Access the credentials_lists

        :returns: twilio.rest.trunking.v1.trunk.credential_list.CredentialListList
        :rtype: twilio.rest.trunking.v1.trunk.credential_list.CredentialListList
        """
        if self._credentials_lists is None:
            self._credentials_lists = CredentialListList(self._version, trunk_sid=self._solution['sid'], )
        return self._credentials_lists

    @property
    def ip_access_control_lists(self):
        """
        Access the ip_access_control_lists

        :returns: twilio.rest.trunking.v1.trunk.ip_access_control_list.IpAccessControlListList
        :rtype: twilio.rest.trunking.v1.trunk.ip_access_control_list.IpAccessControlListList
        """
        if self._ip_access_control_lists is None:
            self._ip_access_control_lists = IpAccessControlListList(
                self._version,
                trunk_sid=self._solution['sid'],
            )
        return self._ip_access_control_lists

    @property
    def phone_numbers(self):
        """
        Access the phone_numbers

        :returns: twilio.rest.trunking.v1.trunk.phone_number.PhoneNumberList
        :rtype: twilio.rest.trunking.v1.trunk.phone_number.PhoneNumberList
        """
        if self._phone_numbers is None:
            self._phone_numbers = PhoneNumberList(self._version, trunk_sid=self._solution['sid'], )
        return self._phone_numbers

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Trunking.V1.TrunkContext {}>'.format(context)


class TrunkInstance(InstanceResource):
    """  """

    class RecordingSetting(object):
        DO_NOT_RECORD = "do-not-record"
        RECORD_FROM_RINGING = "record-from-ringing"
        RECORD_FROM_ANSWER = "record-from-answer"

    def __init__(self, version, payload, sid=None):
        """
        Initialize the TrunkInstance

        :returns: twilio.rest.trunking.v1.trunk.TrunkInstance
        :rtype: twilio.rest.trunking.v1.trunk.TrunkInstance
        """
        super(TrunkInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'account_sid': payload['account_sid'],
            'domain_name': payload['domain_name'],
            'disaster_recovery_method': payload['disaster_recovery_method'],
            'disaster_recovery_url': payload['disaster_recovery_url'],
            'friendly_name': payload['friendly_name'],
            'secure': payload['secure'],
            'recording': payload['recording'],
            'cnam_lookup_enabled': payload['cnam_lookup_enabled'],
            'auth_type': payload['auth_type'],
            'auth_type_set': payload['auth_type_set'],
            'date_created': deserialize.iso8601_datetime(payload['date_created']),
            'date_updated': deserialize.iso8601_datetime(payload['date_updated']),
            'sid': payload['sid'],
            'url': payload['url'],
            'links': payload['links'],
        }

        # Context
        self._context = None
        self._solution = {'sid': sid or self._properties['sid'], }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: TrunkContext for this TrunkInstance
        :rtype: twilio.rest.trunking.v1.trunk.TrunkContext
        """
        if self._context is None:
            self._context = TrunkContext(self._version, sid=self._solution['sid'], )
        return self._context

    @property
    def account_sid(self):
        """
        :returns: The unique ID of the Account that owns this Trunk.
        :rtype: unicode
        """
        return self._properties['account_sid']

    @property
    def domain_name(self):
        """
        :returns: The unique address you reserve on Twilio to which you route your SIP traffic.
        :rtype: unicode
        """
        return self._properties['domain_name']

    @property
    def disaster_recovery_method(self):
        """
        :returns: The HTTP method Twilio will use when requesting the DisasterRecoveryUrl.
        :rtype: unicode
        """
        return self._properties['disaster_recovery_method']

    @property
    def disaster_recovery_url(self):
        """
        :returns: The HTTP URL that Twilio will request if an error occurs while sending SIP traffic towards your configured Origination URL.
        :rtype: unicode
        """
        return self._properties['disaster_recovery_url']

    @property
    def friendly_name(self):
        """
        :returns: A human-readable name for the Trunk.
        :rtype: unicode
        """
        return self._properties['friendly_name']

    @property
    def secure(self):
        """
        :returns: The Secure Trunking  settings for this trunk.
        :rtype: bool
        """
        return self._properties['secure']

    @property
    def recording(self):
        """
        :returns: The recording settings for this trunk.
        :rtype: dict
        """
        return self._properties['recording']

    @property
    def cnam_lookup_enabled(self):
        """
        :returns: The cnam_lookup_enabled
        :rtype: bool
        """
        return self._properties['cnam_lookup_enabled']

    @property
    def auth_type(self):
        """
        :returns: The types of authentication you have mapped to your domain.
        :rtype: unicode
        """
        return self._properties['auth_type']

    @property
    def auth_type_set(self):
        """
        :returns: The auth_type_set
        :rtype: unicode
        """
        return self._properties['auth_type_set']

    @property
    def date_created(self):
        """
        :returns: The date this Activity was created.
        :rtype: datetime
        """
        return self._properties['date_created']

    @property
    def date_updated(self):
        """
        :returns: The date this Activity was updated.
        :rtype: datetime
        """
        return self._properties['date_updated']

    @property
    def sid(self):
        """
        :returns: A 34 character string that uniquely identifies the SIP Trunk in Twilio.
        :rtype: unicode
        """
        return self._properties['sid']

    @property
    def url(self):
        """
        :returns: The URL for this resource, relative to https://trunking.
        :rtype: unicode
        """
        return self._properties['url']

    @property
    def links(self):
        """
        :returns: The links
        :rtype: unicode
        """
        return self._properties['links']

    def fetch(self):
        """
        Fetch a TrunkInstance

        :returns: Fetched TrunkInstance
        :rtype: twilio.rest.trunking.v1.trunk.TrunkInstance
        """
        return self._proxy.fetch()

    def delete(self):
        """
        Deletes the TrunkInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._proxy.delete()

    def update(self, friendly_name=values.unset, domain_name=values.unset,
               disaster_recovery_url=values.unset,
               disaster_recovery_method=values.unset, recording=values.unset,
               secure=values.unset, cnam_lookup_enabled=values.unset):
        """
        Update the TrunkInstance

        :param unicode friendly_name: A human-readable name for the Trunk.
        :param unicode domain_name: The unique address you reserve on Twilio to which you route your SIP traffic.
        :param unicode disaster_recovery_url: The HTTP URL that Twilio will request if an error occurs while sending SIP traffic towards your configured Origination URL.
        :param unicode disaster_recovery_method: The HTTP method Twilio will use when requesting the DisasterRecoveryUrl.
        :param TrunkInstance.RecordingSetting recording: The recording settings for this trunk.
        :param bool secure: The Secure Trunking  settings for this trunk.
        :param bool cnam_lookup_enabled: The cnam_lookup_enabled

        :returns: Updated TrunkInstance
        :rtype: twilio.rest.trunking.v1.trunk.TrunkInstance
        """
        return self._proxy.update(
            friendly_name=friendly_name,
            domain_name=domain_name,
            disaster_recovery_url=disaster_recovery_url,
            disaster_recovery_method=disaster_recovery_method,
            recording=recording,
            secure=secure,
            cnam_lookup_enabled=cnam_lookup_enabled,
        )

    @property
    def origination_urls(self):
        """
        Access the origination_urls

        :returns: twilio.rest.trunking.v1.trunk.origination_url.OriginationUrlList
        :rtype: twilio.rest.trunking.v1.trunk.origination_url.OriginationUrlList
        """
        return self._proxy.origination_urls

    @property
    def credentials_lists(self):
        """
        Access the credentials_lists

        :returns: twilio.rest.trunking.v1.trunk.credential_list.CredentialListList
        :rtype: twilio.rest.trunking.v1.trunk.credential_list.CredentialListList
        """
        return self._proxy.credentials_lists

    @property
    def ip_access_control_lists(self):
        """
        Access the ip_access_control_lists

        :returns: twilio.rest.trunking.v1.trunk.ip_access_control_list.IpAccessControlListList
        :rtype: twilio.rest.trunking.v1.trunk.ip_access_control_list.IpAccessControlListList
        """
        return self._proxy.ip_access_control_lists

    @property
    def phone_numbers(self):
        """
        Access the phone_numbers

        :returns: twilio.rest.trunking.v1.trunk.phone_number.PhoneNumberList
        :rtype: twilio.rest.trunking.v1.trunk.phone_number.PhoneNumberList
        """
        return self._proxy.phone_numbers

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Trunking.V1.TrunkInstance {}>'.format(context)
