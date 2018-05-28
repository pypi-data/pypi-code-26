import os

from vcr import VCR


developer_key = os.environ.get('GOODREADS_API_KEY', 'fuubar')
developer_secret = os.environ.get('GOODREADS_API_SECRET', 'bazqux')


def make_vcr():
    cassette_library_dir = os.path.join(os.path.dirname(__file__),
                                        'fixtures',
                                        'cassettes')
    return VCR(cassette_library_dir=cassette_library_dir,
               filter_query_parameters=[
                   'key',
                   'oauth_consumer_key',
                   'oauth_nonce',
                   'oauth_signature_method',
                   'oauth_timestamp',
                   'oauth_token',
                   'oauth_version',
                   'oauth_signature',
               ],
               record_mode='new_episodes')


vcr = make_vcr()

__all__ = [
    'developer_key',
    'developer_secret',
    'vcr',
]
