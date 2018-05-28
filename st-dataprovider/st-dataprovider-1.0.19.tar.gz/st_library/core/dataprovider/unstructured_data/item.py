# Copyright 2017 Shortest Track Company. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.

from st_library.utils.api_client.services.unstructured_data import UnstructuredDataService


# import of Query is at end of module as we have a circular dependency of
# Query.execute().results -> Table and Table.sample() -> Query

class Item(object):
    """
    Represents an unstructured Item object

    Parameters
    ----------
    matrix_id
    dataset_id

    """

    # Allowed characters in a BigQuery table column name
    _VALID_COLUMN_NAME_CHARACTERS = '_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    # When fetching table contents, the max number of rows to fetch per HTTP request
    _DEFAULT_PAGE_SIZE = 1024

    # Milliseconds per week
    _MSEC_PER_WEEK = 7 * 24 * 3600 * 1000

    def __init__(self, matrix_id=None, dataset_id=None):
        self._service = UnstructuredDataService()
        self._datasets_id = dataset_id
        self._cached_page = None
        self._cached_page_index = 0
        self._schema = None

    def download_file(self, filename=None):
        """
        Download dataset files to disk.

        Parameters
        ----------
        filename
            the name of the dataset files.

        """
        raw_data = self._service.download_object(self._datasets_id, filename)

        with open(filename, 'wb') as f:
            f.write(raw_data)

        return filename

    def upload_file(self, filename=None, filepath=None):
        """
        Upload files to gcs.

        Parameters
        ----------
        filename
            the name of the file.
        filepath
            the path to the file

        """
        return self._service.upload_object(self._datasets_id, filename, filepath)

    def delete_file(self, filename=None):
        """
        Delete files from gcs.

        Parameters
        ----------
        filename
            the name of the file.

        """
        return self._service.delete_object(self._datasets_id, filename)
