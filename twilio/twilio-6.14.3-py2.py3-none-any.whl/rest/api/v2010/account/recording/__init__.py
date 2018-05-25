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
from twilio.rest.api.v2010.account.recording.add_on_result import AddOnResultList
from twilio.rest.api.v2010.account.recording.transcription import TranscriptionList


class RecordingList(ListResource):
    """  """

    def __init__(self, version, account_sid):
        """
        Initialize the RecordingList

        :param Version version: Version that contains the resource
        :param account_sid: The unique sid that identifies this account

        :returns: twilio.rest.api.v2010.account.recording.RecordingList
        :rtype: twilio.rest.api.v2010.account.recording.RecordingList
        """
        super(RecordingList, self).__init__(version)

        # Path Solution
        self._solution = {'account_sid': account_sid, }
        self._uri = '/Accounts/{account_sid}/Recordings.json'.format(**self._solution)

    def stream(self, date_created_before=values.unset, date_created=values.unset,
               date_created_after=values.unset, call_sid=values.unset,
               conference_sid=values.unset, limit=None, page_size=None):
        """
        Streams RecordingInstance records from the API as a generator stream.
        This operation lazily loads records as efficiently as possible until the limit
        is reached.
        The results are returned as a generator, so this operation is memory efficient.

        :param datetime date_created_before: Filter by date created
        :param datetime date_created: Filter by date created
        :param datetime date_created_after: Filter by date created
        :param unicode call_sid: Filter by call_sid
        :param unicode conference_sid: The conference_sid
        :param int limit: Upper limit for the number of records to return. stream()
                          guarantees to never return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, stream() will attempt to read the
                              limit with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.api.v2010.account.recording.RecordingInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(
            date_created_before=date_created_before,
            date_created=date_created,
            date_created_after=date_created_after,
            call_sid=call_sid,
            conference_sid=conference_sid,
            page_size=limits['page_size'],
        )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, date_created_before=values.unset, date_created=values.unset,
             date_created_after=values.unset, call_sid=values.unset,
             conference_sid=values.unset, limit=None, page_size=None):
        """
        Lists RecordingInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param datetime date_created_before: Filter by date created
        :param datetime date_created: Filter by date created
        :param datetime date_created_after: Filter by date created
        :param unicode call_sid: Filter by call_sid
        :param unicode conference_sid: The conference_sid
        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.api.v2010.account.recording.RecordingInstance]
        """
        return list(self.stream(
            date_created_before=date_created_before,
            date_created=date_created,
            date_created_after=date_created_after,
            call_sid=call_sid,
            conference_sid=conference_sid,
            limit=limit,
            page_size=page_size,
        ))

    def page(self, date_created_before=values.unset, date_created=values.unset,
             date_created_after=values.unset, call_sid=values.unset,
             conference_sid=values.unset, page_token=values.unset,
             page_number=values.unset, page_size=values.unset):
        """
        Retrieve a single page of RecordingInstance records from the API.
        Request is executed immediately

        :param datetime date_created_before: Filter by date created
        :param datetime date_created: Filter by date created
        :param datetime date_created_after: Filter by date created
        :param unicode call_sid: Filter by call_sid
        :param unicode conference_sid: The conference_sid
        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of RecordingInstance
        :rtype: twilio.rest.api.v2010.account.recording.RecordingPage
        """
        params = values.of({
            'DateCreated<': serialize.iso8601_datetime(date_created_before),
            'DateCreated': serialize.iso8601_datetime(date_created),
            'DateCreated>': serialize.iso8601_datetime(date_created_after),
            'CallSid': call_sid,
            'ConferenceSid': conference_sid,
            'PageToken': page_token,
            'Page': page_number,
            'PageSize': page_size,
        })

        response = self._version.page(
            'GET',
            self._uri,
            params=params,
        )

        return RecordingPage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of RecordingInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of RecordingInstance
        :rtype: twilio.rest.api.v2010.account.recording.RecordingPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return RecordingPage(self._version, response, self._solution)

    def get(self, sid):
        """
        Constructs a RecordingContext

        :param sid: Fetch by unique recording Sid

        :returns: twilio.rest.api.v2010.account.recording.RecordingContext
        :rtype: twilio.rest.api.v2010.account.recording.RecordingContext
        """
        return RecordingContext(self._version, account_sid=self._solution['account_sid'], sid=sid, )

    def __call__(self, sid):
        """
        Constructs a RecordingContext

        :param sid: Fetch by unique recording Sid

        :returns: twilio.rest.api.v2010.account.recording.RecordingContext
        :rtype: twilio.rest.api.v2010.account.recording.RecordingContext
        """
        return RecordingContext(self._version, account_sid=self._solution['account_sid'], sid=sid, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Api.V2010.RecordingList>'


class RecordingPage(Page):
    """  """

    def __init__(self, version, response, solution):
        """
        Initialize the RecordingPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API
        :param account_sid: The unique sid that identifies this account

        :returns: twilio.rest.api.v2010.account.recording.RecordingPage
        :rtype: twilio.rest.api.v2010.account.recording.RecordingPage
        """
        super(RecordingPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of RecordingInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.api.v2010.account.recording.RecordingInstance
        :rtype: twilio.rest.api.v2010.account.recording.RecordingInstance
        """
        return RecordingInstance(self._version, payload, account_sid=self._solution['account_sid'], )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Api.V2010.RecordingPage>'


class RecordingContext(InstanceContext):
    """  """

    def __init__(self, version, account_sid, sid):
        """
        Initialize the RecordingContext

        :param Version version: Version that contains the resource
        :param account_sid: The account_sid
        :param sid: Fetch by unique recording Sid

        :returns: twilio.rest.api.v2010.account.recording.RecordingContext
        :rtype: twilio.rest.api.v2010.account.recording.RecordingContext
        """
        super(RecordingContext, self).__init__(version)

        # Path Solution
        self._solution = {'account_sid': account_sid, 'sid': sid, }
        self._uri = '/Accounts/{account_sid}/Recordings/{sid}.json'.format(**self._solution)

        # Dependents
        self._transcriptions = None
        self._add_on_results = None

    def fetch(self):
        """
        Fetch a RecordingInstance

        :returns: Fetched RecordingInstance
        :rtype: twilio.rest.api.v2010.account.recording.RecordingInstance
        """
        params = values.of({})

        payload = self._version.fetch(
            'GET',
            self._uri,
            params=params,
        )

        return RecordingInstance(
            self._version,
            payload,
            account_sid=self._solution['account_sid'],
            sid=self._solution['sid'],
        )

    def delete(self):
        """
        Deletes the RecordingInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._version.delete('delete', self._uri)

    @property
    def transcriptions(self):
        """
        Access the transcriptions

        :returns: twilio.rest.api.v2010.account.recording.transcription.TranscriptionList
        :rtype: twilio.rest.api.v2010.account.recording.transcription.TranscriptionList
        """
        if self._transcriptions is None:
            self._transcriptions = TranscriptionList(
                self._version,
                account_sid=self._solution['account_sid'],
                recording_sid=self._solution['sid'],
            )
        return self._transcriptions

    @property
    def add_on_results(self):
        """
        Access the add_on_results

        :returns: twilio.rest.api.v2010.account.recording.add_on_result.AddOnResultList
        :rtype: twilio.rest.api.v2010.account.recording.add_on_result.AddOnResultList
        """
        if self._add_on_results is None:
            self._add_on_results = AddOnResultList(
                self._version,
                account_sid=self._solution['account_sid'],
                reference_sid=self._solution['sid'],
            )
        return self._add_on_results

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Api.V2010.RecordingContext {}>'.format(context)


class RecordingInstance(InstanceResource):
    """  """

    class Status(object):
        IN_PROGRESS = "in-progress"
        PAUSED = "paused"
        STOPPED = "stopped"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"

    class Source(object):
        DIALVERB = "DialVerb"
        CONFERENCE = "Conference"
        OUTBOUNDAPI = "OutboundAPI"
        TRUNKING = "Trunking"
        RECORDVERB = "RecordVerb"
        STARTCALLRECORDINGAPI = "StartCallRecordingAPI"
        STARTCONFERENCERECORDINGAPI = "StartConferenceRecordingAPI"

    def __init__(self, version, payload, account_sid, sid=None):
        """
        Initialize the RecordingInstance

        :returns: twilio.rest.api.v2010.account.recording.RecordingInstance
        :rtype: twilio.rest.api.v2010.account.recording.RecordingInstance
        """
        super(RecordingInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'account_sid': payload['account_sid'],
            'api_version': payload['api_version'],
            'call_sid': payload['call_sid'],
            'conference_sid': payload['conference_sid'],
            'date_created': deserialize.rfc2822_datetime(payload['date_created']),
            'date_updated': deserialize.rfc2822_datetime(payload['date_updated']),
            'duration': payload['duration'],
            'sid': payload['sid'],
            'price': payload['price'],
            'price_unit': payload['price_unit'],
            'status': payload['status'],
            'channels': deserialize.integer(payload['channels']),
            'source': payload['source'],
            'error_code': deserialize.integer(payload['error_code']),
            'uri': payload['uri'],
            'encryption_details': payload['encryption_details'],
            'subresource_uris': payload['subresource_uris'],
        }

        # Context
        self._context = None
        self._solution = {'account_sid': account_sid, 'sid': sid or self._properties['sid'], }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: RecordingContext for this RecordingInstance
        :rtype: twilio.rest.api.v2010.account.recording.RecordingContext
        """
        if self._context is None:
            self._context = RecordingContext(
                self._version,
                account_sid=self._solution['account_sid'],
                sid=self._solution['sid'],
            )
        return self._context

    @property
    def account_sid(self):
        """
        :returns: The unique sid that identifies this account
        :rtype: unicode
        """
        return self._properties['account_sid']

    @property
    def api_version(self):
        """
        :returns: The version of the API in use during the recording.
        :rtype: unicode
        """
        return self._properties['api_version']

    @property
    def call_sid(self):
        """
        :returns: The unique id for the call leg that corresponds to the recording.
        :rtype: unicode
        """
        return self._properties['call_sid']

    @property
    def conference_sid(self):
        """
        :returns: The unique id for the conference associated with the recording, if a conference recording.
        :rtype: unicode
        """
        return self._properties['conference_sid']

    @property
    def date_created(self):
        """
        :returns: The date this resource was created
        :rtype: datetime
        """
        return self._properties['date_created']

    @property
    def date_updated(self):
        """
        :returns: The date this resource was last updated
        :rtype: datetime
        """
        return self._properties['date_updated']

    @property
    def duration(self):
        """
        :returns: The length of the recording, in seconds.
        :rtype: unicode
        """
        return self._properties['duration']

    @property
    def sid(self):
        """
        :returns: A string that uniquely identifies this recording
        :rtype: unicode
        """
        return self._properties['sid']

    @property
    def price(self):
        """
        :returns: The one-time cost of creating this recording.
        :rtype: unicode
        """
        return self._properties['price']

    @property
    def price_unit(self):
        """
        :returns: The currency used in the Price property.
        :rtype: unicode
        """
        return self._properties['price_unit']

    @property
    def status(self):
        """
        :returns: The status of the recording.
        :rtype: RecordingInstance.Status
        """
        return self._properties['status']

    @property
    def channels(self):
        """
        :returns: The number of channels in the final recording file as an integer.
        :rtype: unicode
        """
        return self._properties['channels']

    @property
    def source(self):
        """
        :returns: The way in which this recording was created.
        :rtype: RecordingInstance.Source
        """
        return self._properties['source']

    @property
    def error_code(self):
        """
        :returns: More information about the recording failure, if Status is failed.
        :rtype: unicode
        """
        return self._properties['error_code']

    @property
    def uri(self):
        """
        :returns: The URI for this resource
        :rtype: unicode
        """
        return self._properties['uri']

    @property
    def encryption_details(self):
        """
        :returns: Details for how to decrypt the recording.
        :rtype: dict
        """
        return self._properties['encryption_details']

    @property
    def subresource_uris(self):
        """
        :returns: The subresource_uris
        :rtype: unicode
        """
        return self._properties['subresource_uris']

    def fetch(self):
        """
        Fetch a RecordingInstance

        :returns: Fetched RecordingInstance
        :rtype: twilio.rest.api.v2010.account.recording.RecordingInstance
        """
        return self._proxy.fetch()

    def delete(self):
        """
        Deletes the RecordingInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._proxy.delete()

    @property
    def transcriptions(self):
        """
        Access the transcriptions

        :returns: twilio.rest.api.v2010.account.recording.transcription.TranscriptionList
        :rtype: twilio.rest.api.v2010.account.recording.transcription.TranscriptionList
        """
        return self._proxy.transcriptions

    @property
    def add_on_results(self):
        """
        Access the add_on_results

        :returns: twilio.rest.api.v2010.account.recording.add_on_result.AddOnResultList
        :rtype: twilio.rest.api.v2010.account.recording.add_on_result.AddOnResultList
        """
        return self._proxy.add_on_results

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Api.V2010.RecordingInstance {}>'.format(context)
