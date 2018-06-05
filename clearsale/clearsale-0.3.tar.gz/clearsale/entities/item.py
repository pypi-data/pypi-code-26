# -*- coding: utf-8 -*-
from .base import BaseEntity


class Item(BaseEntity):
    """
    |     Nome     |           Descrição            |     Tipo    |    Tamanho    | Obrigatório |
    |==============|================================|=============|===============|=============|
    | ID           | Código do Produto              | Texto       | 50            | S           |
    | Name         | Nome do Produto                | Texto       | 150           | S           |
    | ItemValue    | Valor Unitário                 | Número      | (20,4)        | S           |
    | Qty          | Quantidade                     | Número      | (1,0)         | S           |
    | Gift         | Presente                       | Número      | (1,0)         | N           |
    | CategoryID   | Código da Categoria do Produto | Número      | (1,0)         | N           |
    | CategoryName | Nome da Categoria do Produto   | Texto       | 200           | N           |

    - XML representação:
        <Item>
            <ID></ID>
            <Name></Name>
            <ItemValue></ItemValue>
            <Qty></Qty>
            <Gift></Gift>
            <CategoryID></CategoryID>
            <CategoryName></CategoryName>
        </Item>
    """

    def __init__(
                    self,
                    ID,
                    Name,
                    ItemValue,
                    Qty,
                    Gift=None,
                    CategoryID=None,
                    CategoryName=None
                ):
        self._data = {}
        self._data["Item"] = {
            "ID": ID,
            "Name": Name,
            "ItemValue": ItemValue,
            "Qty": Qty
        }

        self.set_no_mandatory_fields_values(locals())

    def get_no_mandatory_fields(self):
        return (
            "Gift", "CategoryID", "CategoryName"
        )
