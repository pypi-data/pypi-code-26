import logging

import boto3
from flask import current_app

logger = logging.getLogger(__name__)


def get_aws_session():
    config = current_app.config
    return boto3.Session(
        aws_access_key_id=config.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=config.get('AWS_SECRET_ACCESS_KEY'),
        profile_name=config.get('AWS_PROFILE_NAME'),
        region_name=config.get('AWS_REGION_NAME'))


def get_bucket(name):
    aws = get_aws_session()
    s3 = aws.resource('s3')
    return s3.Bucket(name)


def get_object_data(bucket, key):
    return get_bucket(bucket).Object(key).get()['Body']


def get_object_etag(bucket, key):
    return get_bucket(bucket).Object(key).e_tag


def download_object(bucket, key, stream):
    get_bucket(bucket).Object(key).download_fileobj(stream)
