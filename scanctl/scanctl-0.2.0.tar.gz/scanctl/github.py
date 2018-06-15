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

import github

from scanctl import shell


class ApiClient(github.Github):
    def __init__(self, url, token):
        super().__init__(token, base_url=url)

    def get_orgs(self):
        return github.PaginatedList.PaginatedList(
            github.Organization.Organization,
            self._Github__requester, '/organizations', None)

    def orgs(self):
        yield from self.get_orgs()

    def repos(self, organization):
        org = self.get_organization(organization)
        repos = org.get_repos(type='public')
        yield from repos


async def clone(url, dest):
    cmd = f'git clone --depth=1 {url} {dest}'
    await shell.run(cmd)
