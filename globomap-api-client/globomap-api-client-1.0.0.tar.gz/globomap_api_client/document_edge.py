"""
   Copyright 2018 Globo.com

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from globomap_api_client.document import Document


class DocumentEdge(Document):

    kind = 'edges'

    def post(self, edge, document):
        return super(DocumentEdge, self).post(
            kind=self.kind, collection=edge, document=document)

    def get(self, edge, key):
        return super(DocumentEdge, self).get(
            kind=self.kind, collection=edge, key=key)

    def search_many_coll(self, edges, query=None, per_page=10, page=1):
        uri = '{}/search'.format(self.kind)
        query = self.encoding_params(query)
        params = {
            'query': query,
            'per_page': per_page,
            'edges': edges,
            'page': page
        }
        return self.make_request(method='GET', uri=uri, params=params)

    def search(self, edge, query=None, per_page=10, page=1):
        return super(DocumentEdge, self).search(
            kind=self.kind, collection=edge, query=query,
            per_page=per_page, page=page
        )

    def list(self, edge, per_page=10, page=1):
        return super(DocumentEdge, self).list(
            kind=self.kind, collection=edge, per_page=per_page, page=page)

    def put(self, edge, key, document):
        return super(DocumentEdge, self).put(
            kind=self.kind, collection=edge, key=key, document=document)

    def patch(self, edge, key, document):
        return super(DocumentEdge, self).patch(
            kind=self.kind, collection=edge, key=key, document=document)

    def delete(self, edge, key):
        return super(DocumentEdge, self).delete(
            kind=self.kind, collection=edge, key=key)

    def clear(self, edge, query):
        return super(DocumentEdge, self).clear(
            kind=self.kind, collection=edge, query=query)
