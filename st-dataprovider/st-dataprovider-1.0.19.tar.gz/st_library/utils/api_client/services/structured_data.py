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

import time

from st_library.utils.helpers.store import Store
from st_library.utils.api_client import ApiClient


class StructuredDataService(object):
    """A helper class to issue BigQuery HTTP requests."""

    def sec_tables_get_by_sql(self, sql_statement, start_index=None, max_results=None, page_token=None):
        """Posts a SQL request to retrieve query_job_id

        Args:
            sql_statement: .
        Returns:
            A parsed result object.
        Raises:
            Exception if there is an error performing the operation.
        """
        url = ApiClient.res.sec_get_query_id(Store.config_id)

        body_sql = {'allowLargeResults': False,
                    'query': sql_statement}

        params = {}
        if start_index:
            params['startIndex'] = start_index
        if max_results:
            params['maxResults'] = max_results
        if page_token is not None:
            params['pageToken'] = page_token

        return ApiClient.post(url, json=body_sql, params=params)

    def tables_get(self, dataset_id, matrices_id):
        """Issues a request to retrieve information about a table.

        Args:
          dataset_id: .
          matrices_id: .
        Returns:
          A parsed result object.
        Raises:
          Exception if there is an error performing the operation.
        """
        return ApiClient.get(ApiClient.res.matrices_get(dataset_id, matrices_id))

    def tables_get_by_sql(self, query_job_id):
        """Issues a request to retrieve information about a table.

        Args:
          dataset_id: .
          matrices_id: .
        Returns:
          A parsed result object.
        Raises:
          Exception if there is an error performing the operation.
        """
        return ApiClient.get(ApiClient.res.matrices_get_by_sql(query_job_id))

    def tables_get_by_sql_query(self, query_job_id):
        """Issues a request to retrieve information about a table.

        Args:
          dataset_id: .
          matrices_id: .
        Returns:
          A parsed result object.
        Raises:
          Exception if there is an error performing the operation.
        """
        return ApiClient.post(ApiClient.res.sec_get_query_id(query_job_id))

    def tables_get_parameters(self):
        """Issues a request to retrieve the parameter of the script execution configuration.

        Args:
        Returns:
          A parsed result object.
        Raises:
          Exception if there is an error performing the operation.
        """
        return ApiClient.get(ApiClient.res.sec_get_detail(Store.config_id))

    def tabledata_list(self, config_related, datasetsid, table_name, start_index=None, max_results=None, page_token=None):
        """ Retrieves the contents of a table.

        Args:
          table_name: the name of the table as a tuple of components.
          start_index: the index of the row at which to start retrieval.
          max_results: an optional maximum number of rows to retrieve.
          page_token: an optional token to continue the retrieval.
        Returns:
          A parsed result object.
        Raises:
          Exception if there is an error performing the operation.
        """
        if config_related:
            url = ApiClient.res.sec_matrices_get(Store.config_id, datasetsid, table_name)
        else:
            url = ApiClient.res.matrices_get(datasetsid, table_name)
        params = {}
        if start_index:
            params['startIndex'] = start_index
        if max_results:
            params['maxResults'] = max_results
        if page_token is not None:
            params['pageToken'] = page_token

        return ApiClient.get(url, params=params)

    def tabledata_list_by_sql(self, query_job_id, start_index=None, max_results=None, page_token=None):
        """ Retrieves the contents of a table.

        Args:
          table_name: the name of the table as a tuple of components.
          start_index: the index of the row at which to start retrieval.
          max_results: an optional maximum number of rows to retrieve.
          page_token: an optional token to continue the retrieval.
        Returns:
          A parsed result object.
        Raises:
          Exception if there is an error performing the operation.
        """

        url = ApiClient.res.sec_matrices_get_by_sql(query_job_id)

        params = {}
        if start_index:
            params['startIndex'] = start_index
        if max_results:
            params['maxResults'] = max_results
        if page_token is not None:
            params['pageToken'] = page_token

        return ApiClient.get(url, params=params)

    def tabledata_post(self, datasetsid, table_name, file_name):
        """ Insert the contents of a table.

        Args:
          file_name: the name of the table as a tuple of components.
        Returns:
          A result object.
        Raises:
          Exception if there is an error performing the operation.
        """

        filepath1 = r"/home/st/workspace/st-dataprovider-python/datalab/structured_data/metadata.json"
        filepath2 = file_name
        boundary = '----------%s' % hex(int(time.time() * 1000))
        data = []
        data.append('--%s' % boundary)
        fr1 = open(filepath1, 'rb')
        data.append('Content-Disposition: form-data; name="%s"; filename="metadata.json"' % 'metadata')
        data.append('Content-Type: %s\r\n' % 'application/json')
        data.append(fr1.read())
        fr1.close()
        data.append('--%s' % boundary)
        fr2 = open(filepath2, 'rb')
        data.append('Content-Disposition: form-data; name="%s"; filename="data.csv"' % 'file')
        data.append('Content-Type: %s\r\n' % 'application/vnd.ms-excel')
        data.append(fr2.read())
        fr2.close()
        data.append('--%s--\r\n' % boundary)

        http_body = '\r\n'.join(data)

        headers = {}
        headers['Content-Type'] = 'multipart/form-data; boundary=%s' % boundary

        return ApiClient.post(
            ApiClient.res.matrices_upload(datasetsid, table_name), data=http_body, extra_headers=headers
        )

    def insert_sec_data(self, datasetsid, table_name, json_data):
        """ Insert streams data into matrix.

        Args:
          file_name: the name of the table as a tuple of components.
        Returns:
          A result object.
        Raises:
          Exception if there is an error performing the operation.
        """

        return ApiClient.post(ApiClient.res.sec_matrices_insert(
            Store.config_id, datasetsid, table_name), json=json_data
        )

    def insert_batch_sec_data(self, datasetsid, table_name, file_path, file_name):
        """ Insert streams data into matrix.

        Args:
          file_name: the name of the table as a tuple of components.
        Returns:
          A result object.
        Raises:
          Exception if there is an error performing the operation.
        """

        metadata_file = '/home/st/workspace/dataprovider-py/samples/data/structured_data/metadata_sec.json'
        data_file = file_path + file_name
        boundary = '----------%s' % hex(int(time.time() * 1000))
        data = []
        data.append('--%s' % boundary)
        fr1 = open(metadata_file, 'rb')
        data.append('Content-Disposition: form-data; name="%s"; filename="metadata_sec.json"' % 'metadata')
        data.append('Content-Type: %s\r\n' % 'application/json')
        data.append(fr1.read())
        fr1.close()
        data.append('--%s' % boundary)
        fr2 = open(data_file, 'rb')
        data.append('Content-Disposition: form-data; name="%s"; filename="data.csv"' % 'data')
        data.append('Content-Type: %s\r\n' % 'application/vnd.ms-excel')
        data.append(fr2.read())
        fr2.close()
        data.append('--%s--\r\n' % boundary)

        http_body = '\r\n'.join(data)

        headers = {}
        headers['Content-Type'] = 'multipart/form-data; boundary=%s' % boundary

        return ApiClient.post(ApiClient.res.sec_matrices_batch_insert(
            Store.config_id, datasetsid, table_name), data=http_body, extra_headers=headers
        )
