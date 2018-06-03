import direqt

MOCK_DIREQT_API_KEY = 'mock-api-key'


def test_constructor_defaults():
    d = direqt.DireqtClient(api_key=MOCK_DIREQT_API_KEY)

    assert d.fmt == "RBMV1.0"
    assert d.endpoint == 'https://ads.direqt.io'
    assert d.rbm_endpoint == 'https://rcsbusinessmessaging.googleapis.com'
