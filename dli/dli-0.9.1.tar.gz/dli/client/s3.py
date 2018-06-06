import s3fs
import os
import logging
from dli.client.exceptions import DownloadDestinationNotValid, S3FileDoesNotExist


logger = logging.getLogger(__name__)


class Client:
    """
    A wrapper client providing util methods for s3fs
    """
    def __init__(self, key, secret, token):
        self.s3fs = build_s3fs(key, secret, token)

    def upload_file_to_s3(self, file, s3_location):
        """
        Upload a single file to a specified s3 location. The basename of the
        `file` will be preserved

        :param file: Path to the file
        :type file: str
        :param s3_location: Path to destination directory in S3, file will be
                 stored under <s3_location><filename>
        :return: The full path to the file in S3
        """
        logger.info("Uploading %s to %s", file, s3_location)
        file_name = os.path.basename(file)
        target = f'{s3_location}{file_name}'
        self.s3fs.put(file, target)
        logger.info("done.")
        return target

    def download_file(self, file, destination):
        """
        Helper function to download a file as a stream from S3
        """

        # create parent directories for destination.
        if not os.path.exists(destination):
            os.makedirs(destination, exist_ok=True)

        # We expect destination to be a directory, so check that it is one.
        if not os.path.isdir(destination):
            raise DownloadDestinationNotValid(
                "Expected destination=`%s` to be a directory" % destination
            )

        # does the file exist in s3?
        if not self.s3fs.exists(file):
            logger.warning("Attempted to download `%s` from S3 but the file does not exist", file)
            raise S3FileDoesNotExist("File at path `%s` does not exist." % file)

        # get the bucket and path to the file
        path = file.replace("s3://", "")

        # there are two possibilities
        # 1. Path is a file in s3:
        #    In this case we just download the file directy
        # 2. Path is a key/folder in s3:
        #    In this case we walk all the files and download them individually to the target folder
        # Sadly, s3fs does not expose an `isdir` function but we can determine
        # if the path is a directory or a file by using `exists()` and `walk()` in conjkunction
        children = self.s3fs.walk(path)
        # are we downloading an specific file?
        if not children:
            self.s3fs.get(file, os.path.join(destination, os.path.basename(path)))
            return

        # otherwise we are downloading a directory
        for file in children:
            # get the relative path on where to download the file
            name = os.path.relpath(file, path)
            dest = os.path.join(destination, name)
            # create parent directories for destination.
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            # download the file
            self.s3fs.get(file, dest)

    def upload_files_to_s3(self, files, s3_location, token_refresher=None, num_retries=3):
        """
        Upload multiple files to a specified s3 location. The basename of the
        `files` will be preserved.

        :param files: An list of filepaths
        :type files: list
        :param s3_location: Path to destination directory in S3, file will be
                 stored under <s3_location><filename>
        :param token_refresher: Optional Function to refresh S3 token
        :param num_retries: Optional Number of retries in case of upload failure.
        :return: List of path to the files in S3
        """
        files_to_upload = self._files_to_upload_flattened(files)
        retry_count = 0
        s3_target_locations, files_remaining = self._upload(files_to_upload, s3_location)

        if token_refresher:
            while files_remaining and retry_count < num_retries:
                self._refresh_s3fs_handle(token_refresher())
                s3_destinations, files_remaining = self._upload(files_remaining, s3_location)
                s3_target_locations.extend(s3_destinations)
                retry_count += 1

        return s3_target_locations

    def _refresh_s3fs_handle(self, s3_access_keys):
        self.s3fs = build_s3fs(
            key=s3_access_keys['accessKeyId'],
            secret=s3_access_keys['secretAccessKey'],
            token=s3_access_keys['sessionToken']
        )

    def _upload(self, files, s3_location):
        files_successfully_uploaded = []
        s3_target_locations = []

        try:
            for file in files:
                logger.info("file: %s, s3: %s", file, s3_location)

                s3_target_locations.append(self.upload_file_to_s3(file, s3_location))
                files_successfully_uploaded.append(file)

            return s3_target_locations, []

        except Exception as e:
            logger.error(e)
            return s3_target_locations, [f for f in files if f not in files_successfully_uploaded]

    def _files_to_upload_flattened(self, files):
        files_to_upload = []

        for file in files:
            if not os.path.exists(file):
                raise Exception(f'File / directory specified ({file}) for upload does not exist.')

            if os.path.isfile(file):
                logger.info("detected file: %s", file)
                files_to_upload.append(file)
            elif os.path.isdir(file):
                logger.info("detected directory: %s", file)
                files_to_upload.extend([f'{file}/{f}' for f in os.listdir(file) if os.path.isfile(f'{file}/{f}')])
        return files_to_upload


def build_s3fs(key, secret, token):
    """
    Factory function to create an s3fs client.
    Extracted as a function so that it can
    be easily mocked / patched.
    """
    return s3fs.S3FileSystem(key=key, secret=secret, token=token)
