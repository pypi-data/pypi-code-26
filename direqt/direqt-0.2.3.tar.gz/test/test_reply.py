try:
    import urllib.parse
except ImportError:
    import urlparse

import requests

from conftest import TEST_API_KEY, EXPECTED_INTERACT_URL, TEST_MSISDN


def parse_qs(url):
    """Return URL parameters as a dictionary of name/value pairs."""
    return dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))


def create_mock_rbm_response(req):
    """(Eventually) create a response we would expect from RBM given a request."""
    return req


def test_notify_suggested_reply_provides_proper_default_parameters(direqt, requests_mock):
    """SDK provides expected default parameters fetch endpoint.
    :param direqt.DireqtClient direqt: default Direqt test client
    """

    def verify_request(request):
        """:type request: requests.models.PreparedRequest"""
        qs = parse_qs(request.url)

        assert request.body is None
        assert qs['key'] == TEST_API_KEY
        assert qs['format'] == 'RBMV1.0'
        assert 'adUnit' not in qs
        assert 'targeting' not in qs

        return True

    requests_mock.post(EXPECTED_INTERACT_URL, json={}, additional_matcher=verify_request)

    result = direqt.notify_suggested_reply(TEST_MSISDN, '@direqt-fake-postback-data')

    assert requests_mock.call_count == 1
    assert result is True
