import os

import pytest
from imgservice.app import create_app, setup_logging

setup_logging()


TESTING_ENV = {
    'SECRET_KEY': 'notasecret',

    # TODO: shall we make this configurable?
    'BUCKET_NAMES': 'bkno3-test-imgservice',

    # AWS keys need to be configured on CircleCI
    'AWS_ACCESS_KEY_ID': os.environ.get('AWS_ACCESS_KEY_ID', ''),
    'AWS_SECRET_ACCESS_KEY': os.environ.get('AWS_SECRET_ACCESS_KEY', ''),
}


# ======================================================================
#     IMPORTANT NOTE
# ======================================================================
#
# The test bucket needs to be populated with test data.
# For example (from this repo root):
#
#     aws s3 sync ./test-data/ s3://bkno3-test-imgservice/ --delete
#
# Also, you need to upload a proper bucket policy:
#
#     aws s3api put-bucket-policy \
#         --bucket bkno3-test-imgservice --policy file://s3-policy.json
#
# ======================================================================


@pytest.fixture
def app():
    app = create_app(env=TESTING_ENV)
    app.testing = True
    return app


@pytest.yield_fixture
def app_ctx(app):
    with app.app_context() as ctx:
        yield ctx


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def bucket_name():
    return 'bkno3-test-imgservice'
