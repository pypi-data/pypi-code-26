import logging
from os.path import basename
from hashlib import md5
import boto3

logger = logging.getLogger(__name__)


def get_aws_access_key():
    """
        Retreives the aws access key from
        the local environment
    """
    creds = boto3.Session()._session.get_credentials()
    logger.info("Got aws access key from '%s'", creds.method)
    return creds.access_key


def get_aws_secret_key():
    """
        Retreives the aws access key from
        the local environment
    """
    creds = boto3.Session()._session.get_credentials()
    logger.info("Got aws secret key from '%s'", creds.method)
    return creds.secret_key


def upload_to_s3(local_source_path, s3_uri):
    """
        upload a local file to S3
        Args:
            local_source_path - path to the local file
            s3_uri - S3 uri in the form s3://<bucket>/<prefix>
        Return:
            str - S3 URI generated
    """
    _validate_s3_uri(s3_uri)
    hsh = _md5_file(local_source_path)
    bucket = s3_uri.split('/')[2]
    key = '/'.join(s3_uri.rstrip('/').split('/')[3:] + [hsh, basename(local_source_path)])

    s3 = boto3.resource('s3')
    objs = s3.Bucket(bucket).objects.filter(Prefix=key)
    if len([x for x in objs]) < 1:
        logger.info("File not found on S3, uploading '%s' to S3 with key '%s'" % (local_source_path, key))
        with open(local_source_path, 'rb') as fp:
            s3.Bucket(bucket).put_object(
                Body=fp,
                Key=key
            )
    else:
        logger.info("Found existing key with same MD5 signature at '%s', will skip uploading to S3.", key)

    return 's3://' + bucket + '/' + key


def _validate_s3_uri(s3_uri):
    """
        validates whether an S3 URI is valid
        Args:
            str - S3 URI
    """
    if not s3_uri.startswith("s3://"):
        raise Exception("Invalid S3 URI, must start with 's3://'")
    if not s3_uri.split('/')[2]:
        raise Exception("Invalid S3 URI, bucket cannot be empty")


def _md5_file(path):
    """
        Given a path to a file, will return the
        md5 hash of the file's contents
        Args:
            path - str file path
        Return:
            str - md5 hash
    """
    hsh = md5()
    with open(path, 'rb') as fp:
        for chunk in iter(lambda: fp.read(4096), b''):
            hsh.update(chunk)

    return hsh.hexdigest()
