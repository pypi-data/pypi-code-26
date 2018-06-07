import json
try:
    import urllib.parse
except ImportError:
    import urlparse

import requests

from conftest import TEST_API_KEY, EXPECTED_FETCH_URL, TEST_MSISDN, EXPECTED_AGENT_MESSAGE_URL, \
    EXPECTED_FILE_MESSAGE_URL, TEST_MSISDN_MD5, TEST_SUBSCRIBER_ID


def parse_qs(url):
    """Return URL parameters as a dictionary of name/value pairs."""
    return dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))


def create_mock_rbm_response(req):
    """(Eventually) create a response we would expect from RBM given a request."""
    return req


def test_fetch_provides_proper_default_parameters(direqt, requests_mock):
    """SDK provides expected default parameters fetch endpoint.
    :param direqt.DireqtClient direqt: default Direqt test client
    """

    def verify_request(request):
        """:type request: requests.models.PreparedRequest"""
        qs = parse_qs(request.url)

        assert request.body is None
        assert qs['key'] == TEST_API_KEY
        assert qs['format'] == 'RBMV1.0'
        assert qs['adUnit'] == 'test-ad-unit'
        assert qs['targeting'] == '{}'

        return True

    requests_mock.post(EXPECTED_FETCH_URL, json={}, additional_matcher=verify_request)

    result = direqt.fetch('test-ad-unit', TEST_MSISDN)

    assert requests_mock.call_count == 1
    assert result is False


def test_fetch_handles_empty_response(direqt, requests_mock):
    """handles empty fetch response.
    :param requests_mock.Mocker requests_mock
    :param direqt.DireqtClient direqt
    """
    requests_mock.post(EXPECTED_FETCH_URL, json={})

    result = direqt.fetch('test-ad-unit', TEST_MSISDN)

    assert requests_mock.call_count == 1
    assert result is False


def test_fetch_simple_result(direqt, requests_mock):
    """handles a simple text response.

    Verify that when the Direqt server returns a simple text payload, that payload
    is sent along to RBM as expected.

    :param requests_mock.Mocker requests_mock
    :param direqt.DireqtClient direqt
    """
    rbm_message = {
        'contentMessage': {
            'text': 'Hello, world!'
        }
    }

    direqt_response = {
        'payload': json.dumps(rbm_message)
    }

    def verify_rbm_request(request):
        """:type request: requests.models.PreparedRequest"""
        assert request.body == json.dumps(rbm_message)
        return True

    requests_mock.post(EXPECTED_FETCH_URL, json=direqt_response)  # direqt/fetch
    requests_mock.post(EXPECTED_AGENT_MESSAGE_URL, json=create_mock_rbm_response(rbm_message),
                       additional_matcher=verify_rbm_request)

    result = direqt.fetch('test-ad-unit', TEST_MSISDN)

    assert result is True
    assert requests_mock.call_count == 2


def test_fetch_does_not_send_if_test_set(direqt, requests_mock):
    """Honors the test flag from the server

    Verify that when the Direqt server returns 'isTest', no message
    is sent via RBM.

    :param requests_mock.Mocker requests_mock
    :param direqt.DireqtClient direqt
    """
    rbm_message = {
        'contentMessage': {
            'text': 'Hello, world!'
        }
    }

    direqt_response = {
        'payload': json.dumps(rbm_message),
        'isTest': True
    }

    def verify_rbm_request(request):
        """:type request: requests.models.PreparedRequest"""
        assert False    # should not have been called!

    requests_mock.post(EXPECTED_FETCH_URL, json=direqt_response)  # direqt/fetch
    requests_mock.post(EXPECTED_AGENT_MESSAGE_URL, json={},
                       additional_matcher=verify_rbm_request)

    result = direqt.fetch('test-ad-unit', TEST_MSISDN)

    assert result
    assert requests_mock.call_count == 1    # just the direqt fetch, not the RBM


def test_fetch_media_upload(direqt, requests_mock):
    """Handles a media upload.

    When the fetch response includes a media file, we should upload it.

    :param requests_mock.Mocker requests_mock
    :param direqt.DireqtClient direqt
    """

    file_url = 'http://www.example.com/somefile.jpg'
    thumbnail_url = 'http://www.example.com/somefile-tn.jpg'
    content_description = 'This is a description.'

    expected_rbm_message = {
        'fileUrl': file_url,
        'thumbnailUrl': thumbnail_url,
        'contentDescription': content_description
    }

    # N.B. Currently, 'payload' is a string, while 'media' is JSON...
    direqt_response = {
        'media': [
            {'file_url': file_url, 'thumbnail_url': thumbnail_url, 'content_description': content_description},
        ]
    }

    def verify_rbm_request(request):
        """:type request: requests.models.PreparedRequest"""
        assert request.body == json.dumps(expected_rbm_message)
        return True

    requests_mock.post(EXPECTED_FETCH_URL, json=direqt_response)  # direqt/fetch
    requests_mock.post(EXPECTED_FILE_MESSAGE_URL, json=create_mock_rbm_response(expected_rbm_message),
                       additional_matcher=verify_rbm_request)

    rbm_called = False
    result = direqt.fetch('test-ad-unit', TEST_MSISDN)

    assert requests_mock.call_count == 2


def test_fetch_provides_proper_sms_parameters(direqt_sms, requests_mock):
    """SDK provides expected default parameters fetch endpoint.
    :param direqt.DireqtClient direqt: default Direqt test client
    """

    def verify_request(request):
        """:type request: requests.models.PreparedRequest"""
        qs = parse_qs(request.url)

        assert request.body is None
        assert qs['key'] == TEST_API_KEY
        assert qs['format'] == 'SMS'
        assert qs['adUnit'] == 'test-ad-unit'
        assert qs['subscriber'] == TEST_MSISDN_MD5
        assert qs['targeting'] == '{}'

        return True

    requests_mock.post(EXPECTED_FETCH_URL, json={}, additional_matcher=verify_request)

    result = direqt_sms.fetch('test-ad-unit', TEST_MSISDN)

    assert requests_mock.call_count == 1
    assert result is False


def test_fetch_uses_supplied_subscriber_id(direqt_sms, requests_mock):
    """SDK provides expected default parameters fetch endpoint.
    :param direqt.DireqtClient direqt: default Direqt test client
    """

    def verify_request(request):
        """:type request: requests.models.PreparedRequest"""
        qs = parse_qs(request.url)
        assert qs['subscriber'] == TEST_SUBSCRIBER_ID
        return True

    requests_mock.post(EXPECTED_FETCH_URL, json={}, additional_matcher=verify_request)

    result = direqt_sms.fetch('test-ad-unit', subscriber_id=TEST_SUBSCRIBER_ID)

    assert requests_mock.call_count == 1
    assert result is False


def test_fetch_uses_supplied_subscriber_id_when_msisdn_provided(direqt_sms, requests_mock):
    """SDK provides expected default parameters fetch endpoint.
    :param direqt.DireqtClient direqt: default Direqt test client
    """

    def verify_request(request):
        """:type request: requests.models.PreparedRequest"""
        qs = parse_qs(request.url)
        assert qs['subscriber'] == TEST_SUBSCRIBER_ID
        return True

    requests_mock.post(EXPECTED_FETCH_URL, json={}, additional_matcher=verify_request)

    result = direqt_sms.fetch('test-ad-unit', TEST_MSISDN, subscriber_id=TEST_SUBSCRIBER_ID)

    assert requests_mock.call_count == 1
    assert result is False


def test_fetch_returns_proper_sms_response(direqt_sms, requests_mock):
    """fetch() returns proper response object for SMS.
    :param direqt.DireqtClient direqt_sms: default Direqt test client configured for SMS
    """

    def verify_request(request):
        """:type request: requests.models.PreparedRequest"""
        qs = parse_qs(request.url)

        assert request.body is None
        assert qs['key'] == TEST_API_KEY
        assert qs['format'] == 'SMS'
        assert qs['adUnit'] == 'test-ad-unit'
        assert qs['targeting'] == '{}'

        return True

    requests_mock.post(EXPECTED_FETCH_URL, json={'payload': 'This is test payload', 'messageId': 'test-message-id'}, additional_matcher=verify_request)

    result = direqt_sms.fetch('test-ad-unit', TEST_MSISDN)

    assert requests_mock.call_count == 1
    assert result is not False
    assert result['payload'] == 'This is test payload'
    assert result['message_id'] == 'test-message-id'


def test_fetch_returns_proper_sms_response_with_custom_properties(direqt_sms, requests_mock):
    """fetch() returns proper response object for SMS.
    :param direqt.DireqtClient direqt_sms: default Direqt test client configured for SMS
    """
    response_json = {
        'payload': 'This is test payload',
        'messageId': 'test-message-id',
        'properties': {
            'foo': 'foo-value',
            'bar': 'bar-value',
            'fff': 42
        }
    }

    requests_mock.post(EXPECTED_FETCH_URL, json=response_json)

    result = direqt_sms.fetch('test-ad-unit', TEST_MSISDN)

    assert requests_mock.call_count == 1
    assert 'properties' in result
    properties = result['properties']
    assert properties['foo'] == 'foo-value'
    assert properties['bar'] == 'bar-value'
    assert properties['fff'] == 42


def test_fetch_sets_is_test_flag_to_false_by_default(direqt_sms, requests_mock):
    """fetch() sets 'is_test' property to false by default
    :param direqt.DireqtClient direqt_sms: default Direqt test client configured for SMS
    """
    response_json = {
        'payload': 'This is test payload',
        'messageId': 'test-message-id',
        'properties': {
            'foo': 'foo-value',
            'bar': 'bar-value',
            'fff': 42
        }
    }

    requests_mock.post(EXPECTED_FETCH_URL, json=response_json)

    result = direqt_sms.fetch('test-ad-unit', TEST_MSISDN)

    assert requests_mock.call_count == 1
    assert 'is_test' in result
    assert not result['is_test']


def test_fetch_sets_is_test_flag_to_false_for_false_value(direqt_sms, requests_mock):
    """fetch() sets 'is_test' property to false by default
    :param direqt.DireqtClient direqt_sms: default Direqt test client configured for SMS
    """
    response_json = {
        'payload': 'This is test payload',
        'messageId': 'test-message-id',
        'properties': {
            'foo': 'foo-value',
            'bar': 'bar-value',
            'fff': 42
        },
        'isTest': False
    }

    requests_mock.post(EXPECTED_FETCH_URL, json=response_json)

    result = direqt_sms.fetch('test-ad-unit', TEST_MSISDN)

    assert requests_mock.call_count == 1
    assert 'is_test' in result
    assert not result['is_test']


def test_fetch_sets_is_test_flag_to_true(direqt_sms, requests_mock):
    """fetch() sets 'is_test' property to false by default
    :param direqt.DireqtClient direqt_sms: default Direqt test client configured for SMS
    """
    response_json = {
        'payload': 'This is test payload',
        'messageId': 'test-message-id',
        'properties': {
            'foo': 'foo-value',
            'bar': 'bar-value',
            'fff': 42
        },
        'isTest': True
    }

    requests_mock.post(EXPECTED_FETCH_URL, json=response_json)

    result = direqt_sms.fetch('test-ad-unit', TEST_MSISDN)

    assert requests_mock.call_count == 1
    assert 'is_test' in result
    assert result['is_test']


def test_fetch_does_not_leak_msisdn(direqt, requests_mock):
    """Msisdn supplied to fetch should never appear in a server request.
    :param direqt.DireqtClient direqt: default Direqt test client
    """

    def verify_request(request):
        """:type request: requests.models.PreparedRequest"""
        qs = parse_qs(request.url)

        assert request.body is None
        for k in qs:
            assert TEST_MSISDN not in qs[k]

        return True

    requests_mock.post(EXPECTED_FETCH_URL, json={}, additional_matcher=verify_request)

    result = direqt.fetch('test-ad-unit', TEST_MSISDN)

    assert requests_mock.call_count == 1
    assert result is False


def test_fetch_invokes_custom_url_shortener(direqt_sms, requests_mock):
    """fetch() invokes custom shortener for SMS url, and requests longUrl.
    :param direqt.DireqtClient direqt_sms: default Direqt test client configured for SMS
    """

    def verify_request(request):
        """:type request: requests.models.PreparedRequest"""
        qs = parse_qs(request.url)
        assert qs['longUrl'] == 'true'
        return True

    requests_mock.post(EXPECTED_FETCH_URL, json={
        'payload': 'This is test payload http://www.example.com/long/url/here',
        'messageId': 'test-message-id'}, additional_matcher=verify_request)

    def custom_url_shortener(url):
        return 'https://ex.co/short/url'

    result = direqt_sms.fetch('test-ad-unit', TEST_MSISDN, url_shortener=custom_url_shortener)

    assert requests_mock.call_count == 1
    assert result is not False
    assert result['payload'] == 'This is test payload https://ex.co/short/url'
    assert result['message_id'] == 'test-message-id'


def test_fetch_with_url_shortener_but_no_returned_link(direqt_sms, requests_mock):
    """fetch() behaves as expected when custom shortener specified and no link in returned payload.
    :param direqt.DireqtClient direqt_sms: default Direqt test client configured for SMS
    """
    requests_mock.post(EXPECTED_FETCH_URL, json={
        'payload': 'This payload has no link',
        'messageId': 'test-message-id'})

    def custom_url_shortener(url):
        return 'https://ex.co/short/url'

    result = direqt_sms.fetch('test-ad-unit', TEST_MSISDN, url_shortener=custom_url_shortener)

    assert requests_mock.call_count == 1
    assert result is not False
    assert result['payload'] == 'This payload has no link'

