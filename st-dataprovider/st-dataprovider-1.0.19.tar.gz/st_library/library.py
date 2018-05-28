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
from st_library.core.dataprovider.structured_data.structured_data import StructuredData
from st_library.core.dataprovider.unstructured_data.unstructured_data import UnstructuredData
from st_library.core.logger.logger import Logger
from st_library.core.metadata.metadata import _METADATA
from st_library.utils.databases.databases import Databases
from st_library.utils.generics.singleton import Singleton
from st_library.utils.helpers.store import Store


__all__ = ('Library',)


class Library(Singleton):
    """
    The Library containing all the required functionality for work with Shortest Track Services.

    Attributes
    ----------
    struct_data : :class:`~st_library.core.dataprovider.structured_data.structured_data.StructuredData`
        A Category for work with structured data

    unstruct_data : :class:`~st_library.core.dataprovider.unstructured_data.unstructured_data.UnstructuredData`
        A Category for work with unstructured data

    logger : :class:`~st_library.core.logger.logger.Logger`
        A Category for log messages

    metadata : :class:`~st_library.core.metadata.metadata.Metadata`
        A Category for work with metadata

    config_id : str
        ID of the Script Execution Configuration for current Environment

    token : str
        The Token for current Environment

    performance_id : str
        ID of the Performance for current Environment

    Methods
    -------
    set_config_id(config_id='1686408f-2fc5-4657-b0d3-1c5c6b8e1ad7')
        Set the ID of Script Execution Configuration for current Environment

    set_token(token='1686408f-2fc5-4657-b0d3-1c5c6b8e1ad7')
        Set the Token for current Environment

    Examples
    --------
        >>> from st_library import Library
        >>> st_lib = Library()
        >>> st_lib.set_config_id('1686408f-2fc5-4657-b0d3-1c5c6b8e1ad7')
        >>> param = st_lib.metadata.get_parameter_value('foo')
        >>> table = st_lib.struct_data.Table('bar', 'baz', 'bar-baz')
        >>> table.upload_data('/foo/bar.csv')

    """

    def __init__(self):
        self.struct_data = StructuredData()
        self.unstruct_data = UnstructuredData()
        self.logger = Logger()
        self.metadata = _METADATA
        self.databases = Databases()

    @property
    def config_id(self):
        return Store.config_id

    def set_config_id(self, config_id):
        Store.config_id = config_id

    @property
    def token(self):
        return Store.token

    def set_token(self, token):
        Store.token = token

    @property
    def performance_id(self):
        return Store.performance_id
