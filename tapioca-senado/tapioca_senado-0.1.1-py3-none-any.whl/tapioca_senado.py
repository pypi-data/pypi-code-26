# coding: utf-8

from tapioca import (
    TapiocaAdapter, generate_wrapper_from_adapter
)
from tapioca.adapters import XMLAdapterMixin

from .resource_mapping import RESOURCE_MAPPING


class SenadoClientAdapter(XMLAdapterMixin, TapiocaAdapter):
    resource_mapping = RESOURCE_MAPPING
    api_root = 'http://legis.senado.gov.br/dadosabertos'

    def get_iterator_list(self, response_data):
        return response_data

    def get_iterator_next_request_kwargs(self,
                                         iterator_request_kwargs,
                                         response_data,
                                         response):
        pass

    def response_to_native(self, response):
        if response.content.strip():
            return super(SenadoClientAdapter, self).response_to_native(response)


Senado = generate_wrapper_from_adapter(SenadoClientAdapter)

