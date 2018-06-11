# -*- coding: utf-8 -*-
from .base import BaseCustomer


class BillingData(BaseCustomer):
    """
    |    Nome   |     Descrição      | Tipo |       Tamanho        | Obrigatório |
    |===========|====================|======|======================|=============|
    | BirthDate | Data de Nascimento | Data | (yyyy-mmddThh:mm:ss) | S           |
    """

    def __init__(self, BirthDate, *args, **kwargs):
        kwargs["BirthDate"] = BirthDate
        super(BillingData, self).__init__(*args, **kwargs)
        self._data_temp = self._data
        self._data = {}
        self._data["BillingData"] = self._data_temp
