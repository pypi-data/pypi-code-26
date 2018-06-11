# -*- coding: utf-8 -*-
from .base import BaseCustomer


class ShippingData(BaseCustomer):
    """
    |    Nome   |     Descrição      | Tipo |       Tamanho        | Obrigatório |
    |===========|====================|======|======================|=============|
    | BirthDate | Data de Nascimento | Data | (yyyy-mmddThh:mm:ss) | N           |
    """
    def __init__(self, *args, **kwargs):
        super(ShippingData, self).__init__(*args, **kwargs)
        self._data_temp = self._data
        self._data = {}
        self._data["ShippingData"] = self._data_temp
