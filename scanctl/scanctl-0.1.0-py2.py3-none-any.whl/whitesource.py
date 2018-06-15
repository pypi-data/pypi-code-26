# -*- coding: utf-8 -*-

# Copyright 2018 Spotify AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import os.path

import attr
import requests

from scanctl import shell


@attr.s
class ApiClient:
    _sess = attr.ib(init=False, factory=lambda: requests.Session())

    url = attr.ib()
    token = attr.ib()

    def post(self, params):
        data = {'orgToken': self.token, **params}
        resp = self._sess.post(self.url, json=data)
        if resp.status_code != 200:
            resp.raise_for_status()
        return resp.json()

    def products(self):
        params = {'requestType': 'getAllProducts'}
        products = self.post(params).get('products', [])
        for p in products:
            yield Product(self, p['productToken'], p['productName'])

    def projects(self, product):
        params = {'requestType': 'getAllProjects',
                  'productToken': product.token}
        projects = self.post(params).get('projects', [])
        for p in projects:
            yield Project(self, product,
                          p['projectToken'], p['projectName'])


@attr.s(frozen=True)
class Product:
    client = attr.ib()
    token = attr.ib()
    name = attr.ib()

    def __str__(self):
        return self.name

    def projects(self):
        return self.client.projects(self)

    def delete(self):
        logging.info(f'delete {self}')
        params = {'requestType': 'deleteProduct', 'productToken': self.token}
        return self.client.post(params)


@attr.s(frozen=True)
class Project:
    client = attr.ib()
    product = attr.ib()
    token = attr.ib()
    name = attr.ib()

    def __str__(self):
        return self.name

    def delete(self):
        logging.info(f'delete {self}')
        params = {'requestType': 'deleteProject',
                  'productToken': self.product.token,
                  'projectToken': self.token,
                  }
        return self.client.post(params)


@attr.s
class FsAgent:
    token = attr.ib()
    jar = attr.ib(os.path.join(os.getcwd(), 'bin', 'fs-agent.jar'))
    config = attr.ib(os.path.join(os.getcwd(), 'etc', 'whitesource.config'))

    async def run(self, org, repo, path):
        cmd = f'java -jar {self.jar} -c {self.config} -apiKey {self.token} '\
              f'-product {org} -project {repo} -d {path}'
        await shell.run(cmd)
