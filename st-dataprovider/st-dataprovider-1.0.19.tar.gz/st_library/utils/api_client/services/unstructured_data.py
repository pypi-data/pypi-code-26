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

"""Implements BigQuery HTTP API wrapper."""

import os

from requests_toolbelt.multipart.encoder import MultipartEncoder

from st_library.utils.api_client import ApiClient


class UnstructuredDataService(object):
    """A helper class to issue BigQuery HTTP requests."""

    def __init__(self):
        """Initializes the BigQuery helper with context information.

        """

    def tables_get(self, table_name, matrices_id):
        """Issues a request to retrieve information about a table.

        Args:
          table_name: a tuple representing the full name of the table.
        Returns:
          A parsed result object.
        Raises:
          Exception if there is an error performing the operation.
        """

        return ApiClient.get(ApiClient.res.object(table_name, matrices_id))

    def download_object(self, datasetsid, file_name):
        """ Download an object.

        Args:
          datasetsid: the id of the dataset.
          file_name: the name of the dataset files.
        Returns:
          A url for downloading object.
        Raises:
          Exception if there is an error performing the operation.
        """

        return ApiClient.get(ApiClient.res.object_download(datasetsid, file_name), raw_response=True)

    def upload_object(self, datasetsid, file_name, file_path):
        """ Upload file to gcs.

        Args:
          file_name: the name of the file.
          file_path: the path of the file.
        Returns:
          A result object.
        Raises:
          Exception if there is an error performing the operation.
        """

        path = os.path.join(file_path, file_name)

        with open(path, 'rb') as f:
            multipart_data = MultipartEncoder(
                fields={
                    # a file upload field
                    'file': (file_name, f, 'text/plain')
                }
            )
            headers = dict()
            headers['Content-Type'] = multipart_data.content_type

            return ApiClient.post(ApiClient.res.object(datasetsid, file_name), data=multipart_data,
                                  extra_headers=headers)

    def delete_object(self, datasetsid, file_name):
        """ Delete an object.

        Args:
          datasetsid: the id of the dataset.
          file_name: the name of the dataset files.
        Returns:
          A url for downloading object.
        Raises:
          Exception if there is an error performing the operation.
        """

        return ApiClient.delete(ApiClient.res.object(datasetsid, file_name))
