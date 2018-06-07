import io
import logging
from contextlib import contextmanager
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError
from werkzeug.exceptions import Forbidden, NotFound

logger = logging.getLogger(__name__)


class S3BucketLoader:
    def __init__(self, *,
                 aws_access_key_id=None,
                 aws_secret_access_key=None,
                 aws_profile_name=None,
                 aws_region_name=None,
                 bucket_names=None):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_profile_name = aws_profile_name
        self.aws_region_name = aws_region_name
        self.bucket_names = bucket_names

    def _parse_url(self, url):
        parsed = urlparse(url)
        return parsed.hostname, parsed.path.strip('/')

    def __call__(self, name):
        return self.load_image(name)

    def load_image(self, url):
        bucket, key = self._parse_url(url)

        if ((self.bucket_names is not None) and
                (bucket not in self.bucket_names)):

            logger.warning(
                'Attempt to access unauthorized bucket: {bucket}'
                .format(bucket=bucket))

            raise Forbidden('Cannot access bucket {}'.format(bucket))

        # with handle_client_error():
        #     etag = _get_object_etag(bucket, key)

        input_stream = io.BytesIO()

        with handle_client_error():
            self._download_object(bucket, key, input_stream)

        return input_stream

    def _get_aws_session(self):
        return boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            profile_name=self.profile_name,
            region_name=self.region_name)

    def _get_bucket(self, name):
        aws = self._get_aws_session()
        s3 = aws.resource('s3')
        return s3.Bucket(name)

    def _get_object_data(self, bucket, key):
        return self._get_bucket(bucket).Object(key).get()['Body']

    def _get_object_etag(self, bucket, key):
        return self._get_bucket(bucket).Object(key).e_tag

    def _download_object(self, bucket, key, stream):
        self._get_bucket(bucket).Object(key).download_fileobj(stream)


@contextmanager
def handle_client_error():
    try:
        yield
    except ClientError as e:
        logger.warning('Error: {}'.format(e.response))
        err_code = e.response['Error']['Code']
        if err_code in ('404', '403'):
            logger.exception('Got error response from S3 (%s)', err_code)
            # TODO: serve default image instead
            raise NotFound('Image not found')

        # Unhandled exception -> make sure it gets logged
        raise
