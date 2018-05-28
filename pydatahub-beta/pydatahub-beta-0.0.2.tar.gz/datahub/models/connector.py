#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from __future__ import absolute_import

import abc
import json
from enum import Enum

import six


class ConnectorType(Enum):
    """
    ConnectorType enum class, there are: ``sink_odps``
    """
    SINK_ODPS = 'sink_odps'


class ConnectorState(Enum):
    """
    ConnectorState enum class, there are: ``CONNECTOR_CREATED``, ``CONNECTOR_RUNNING``, ``CONNECTOR_PAUSED``
    """
    CONNECTOR_CREATED = 'CONNECTOR_CREATED'
    CONNECTOR_RUNNING = 'CONNECTOR_RUNNING'
    CONNECTOR_PAUSED = 'CONNECTOR_PAUSED'


@six.add_metaclass(abc.ABCMeta)
class ConnectorConfig(object):
    """
    Connector config class
    """

    @abc.abstractmethod
    def to_json(self):
        pass

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, dict_):
        pass


class OdpsConnectorConfig(ConnectorConfig):
    """
    Connector config for odps

    Members:
        project_name (:class:`str`): odps project name

        table_name (:class:`str`): odps table name

        odps_endpoint (:class:`str`): odps endpoint

        tunnel_endpoint (:class:`str`): tunnel endpoint

        access_id (:class:`str`): odps access id

        access_key (:class:`str`): odps access key
    """

    __slots__ = ('_project_name', '_table_name', '_odps_endpoint',
                 '_tunnel_endpoint', '_access_id', '_access_key')

    def __init__(self, project_name, table_name, odps_endpoint,
                 tunnel_endpoint, access_id='', access_key=''):
        self._project_name = project_name
        self._table_name = table_name
        self._odps_endpoint = odps_endpoint
        self._tunnel_endpoint = tunnel_endpoint
        self._access_id = access_id
        self._access_key = access_key

    @property
    def project_name(self):
        return self._project_name

    @project_name.setter
    def project_name(self, value):
        self._project_name = value

    @property
    def table_name(self):
        return self._table_name

    @table_name.setter
    def table_name(self, value):
        self._table_name = value

    @property
    def odps_endpoint(self):
        return self._odps_endpoint

    @odps_endpoint.setter
    def odps_endpoint(self, value):
        self._odps_endpoint = value

    @property
    def tunnel_endpoint(self):
        return self._tunnel_endpoint

    @tunnel_endpoint.setter
    def tunnel_endpoint(self, value):
        self._tunnel_endpoint = value

    @property
    def access_id(self):
        return self._access_id

    @access_id.setter
    def access_id(self, value):
        self._access_id = value

    @property
    def access_key(self):
        return self._access_key

    @access_key.setter
    def access_key(self, value):
        self._access_key = value

    def to_json(self):
        return {
            "Project": self._project_name,
            "Table": self._table_name,
            "OdpsEndpoint": self._odps_endpoint,
            "TunnelEndpoint": self._tunnel_endpoint,
            "AccessId": self._access_id,
            "AccessKey": self._access_key
        }

    @classmethod
    def from_dict(cls, dict_):
        access_id = dict_['AccessId'] if 'AccessId' in dict_ else ''
        access_key = dict_['AccessKey'] if 'AccessKey' in dict_ else ''
        return cls(dict_['Project'], dict_['Table'], dict_['OdpsEndpoint'],
                   dict_['TunnelEndpoint'], access_id, access_key)

    def __repr__(self):
        return json.dumps(self.to_json())
