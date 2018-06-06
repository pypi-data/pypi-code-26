import logging
import os
import tempfile
import s3fs
import socket

from dli.client import s3
from unittest import TestCase
from dli.client.s3 import Client
from dli.client.exceptions import S3FileDoesNotExist, DownloadDestinationNotValid
from mock import patch


logger = logging.getLogger(__name__)


def build_fake_s3fs(key, secret, token):
    # Nasty: Resolve the hostname so that the we connect 
    # using the ip address instead of the hostname
    # this is due a limitation in fake-s3, read more here:
    # https://github.com/jubos/fake-s3/issues/17
    s3_hostname = socket.gethostbyname(os.environ.get("FAKE_S3_HOST", "localhost"))
    s3_port = os.environ.get("FAKE_S3_PORT", 4569)

    return s3fs.S3FileSystem(
        key=key,
        secret=secret,
        token=token,
        client_kwargs={
            "endpoint_url": "http://%s:%s" % (s3_hostname, s3_port)
        }
    )


class S3ClientTestCase(TestCase):

    def setUp(self):
        self.target = Client("key", "secret", "token")
        self.target.s3fs = build_fake_s3fs("key", "sectet", "token")

    def test_download_file_validates_file_exists_in_s3(self):
        with self.assertRaises(S3FileDoesNotExist):
            with tempfile.TemporaryDirectory() as dest:
                self.target.download_file("s3://unknown/file", dest)

    def test_download_file_validates_destination_is_a_directory(self):
        with self.assertRaises(DownloadDestinationNotValid):
            with tempfile.TemporaryFile() as cm:
                self.target.download_file("s3://some/file", cm.name)

    def test_download_file_creates_destination_directory_if_it_doesnt_exist(self):
        # upload a sample file
        self.target.s3fs.put(
            __file__,
            os.path.join("s3://bucket/location/", os.path.basename(__file__))
        )

        # assert we can downlaod it
        with tempfile.TemporaryDirectory() as dest:
            dest = os.path.join(dest, "dir1", "dir2")
            self.target.download_file(
                "s3://bucket/location/test_s3_client.py",
                dest
            )

            # directories were created
            self.assertTrue(os.path.exists(dest) and os.path.isdir(dest))
            self.assertTrue(os.path.exists(os.path.join(dest, "test_s3_client.py")))

    def test_download_file_can_download_folders(self):
        # upload a some sample files
        self.target.s3fs.put(__file__, "s3://bucket/tdfcdf/file1.txt")
        self.target.s3fs.put(__file__, "s3://bucket/tdfcdf/subdir/file2.txt")
        self.target.s3fs.put(__file__, "s3://bucket/tdfcdf/subdir/subdir/file3.txt")

        with tempfile.TemporaryDirectory() as dest:
            self.target.download_file("s3://bucket/tdfcdf", dest)

            self.assertTrue(os.path.exists(dest))
            self.assertTrue(os.path.exists(os.path.join(dest, "file1.txt")))
            self.assertTrue(os.path.exists(os.path.join(dest, "subdir", "file2.txt")))
            self.assertTrue(os.path.exists(os.path.join(dest, "subdir", "subdir", "file3.txt")))