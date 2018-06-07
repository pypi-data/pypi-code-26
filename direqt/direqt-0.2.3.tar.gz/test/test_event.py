try:
    import urllib.parse
except ImportError:
    import urlparse

from conftest import TEST_API_KEY, EXPECTED_EVENT_URL


def parse_qs(url):
    """Return URL parameters as a dictionary of name/value pairs."""
    return dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))

def test_track_custom_event_provides_proper_parameters(direqt, requests_mock):
    """SDK provides expected parameters for custom event endpoint.
    :param direqt.DireqtClient direqt: default Direqt test client
    """
    mock_response = {
        'messageId': 'xx',
        'eventName': 'xx',
        'eventData': { 'foo': 'bar' }
    }
    adapter = requests_mock.post(EXPECTED_EVENT_URL, json=mock_response)

    custom_event_data = {
        'thing_one': 'foo',
        'thing_two': 'bar'
    }
    result = direqt.track_custom_event('test-message-id', 'custom-event-name', custom_event_data)

    assert adapter.call_count == 1
    qs = parse_qs(adapter.last_request.url)
    assert qs['key'] == TEST_API_KEY

    request_body = adapter.last_request.json()
    assert request_body['messageId'] == 'test-message-id'
    assert request_body['eventName'] == 'custom-event-name'
    assert request_body['eventData']['thing_one'] == 'foo'
    assert request_body['eventData']['thing_two'] == 'bar'

    assert result == mock_response

