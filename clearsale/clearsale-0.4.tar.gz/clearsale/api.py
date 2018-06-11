# -*- coding: utf-8 -*-
from suds.client import Client
from .responses import OrderStatusResponse, SendOrdersResponse


class ClearSaleConnector():
    def __init__(self, entity_code, use_sandbox=True, **extra_params_connection):
        self._entity_code = entity_code
        self._extra_params_connection = extra_params_connection
        self._ws_url = "https://homologacao.clearsale.com.br/integracaov2/service.asmx?wsdl" if use_sandbox \
            else "https://www.clearsale.com.br/integracaov2/service.asmx?wsdl"

    def get_ws_client(self):
        return Client(self._ws_url, **self._extra_params_connection)

    def get_entity_code(self):
        return self._entity_code


class ClearSaleService():
    def __init__(self, clearsale_connector, *args, **kwargs):
        self._connector = clearsale_connector

    def send_orders(self, orders):
        xml = u"<ClearSale>{0}</ClearSale>".format(orders.get_xml())
        xml_ret = self._connector.get_ws_client().service.SendOrders(
            self._connector.get_entity_code(), xml)
        return SendOrdersResponse(xml_ret.format())

    def get_order_status(self, order_id):
        xml_ret = self._connector.get_ws_client().service.GetOrderStatus(
            self._connector.get_entity_code(), order_id)
        return OrderStatusResponse(xml_ret.format())

    def get_connector(self):
        return self._connector

    def set_connector(self, clearsale_connector):
        self._connector = clearsale_connector
