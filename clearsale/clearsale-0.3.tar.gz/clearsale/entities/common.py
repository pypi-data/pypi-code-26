# -*- coding: utf-8 -*-
from .base import BaseEntity


class FingerPrint(BaseEntity):
    """
    |    Nome   |                Descrição                 |  Tipo  | Tamanho  | Obrigatório |
    |===========|==========================================|========|==========|=============|
    | SessionID | Identificador único da sessão do usuário | String |      128 | S           |

    <FingerPrint>
        <SessionID></SessionID>
    </FingerPrint>
    """

    def __init__(self, SessionID):
        self._data = {}
        self._data["FingerPrint"] = {"SessionID": SessionID}


class Address(BaseEntity):
    """
    |     Nome    |                 Descrição                 |     Tipo    |    Tamanho    | Obrigatório |
    |=============|===========================================|=============|===============|=============|
    | Street      | Nome do logradouro (Sem abreviações)      | Texto       |           200 | S           |
    | Number      | Número do Endereço                        | Texto       |            15 | S           |
    | Comp        | Complemento do Endereço (Sem abreviações) | Texto       |           250 | N           |
    | County      | Bairro do Endereço (Sem abreviações)      | Texto       |           150 | S           |
    | City        | Cidade do Endereço (Sem abreviações)      | Texto       |           150 | S           |
    | State       | Sigla do Estado do Endereço - UF          | Texto       |             2 | S           |
    | Country     | Pais do Endereço (Sem abreviações)        | Texto       |           150 | N           |
    | ZipCode     | CEP do Endereço                           | Número      |            10 | S           |
    | Reference   | Referência do Endereço (Sem abreviações)  | Texto       |           250 | N           |

    - XML representação:
        <Address>
            <Street></Street>
            <Number></Number>
            <Comp></Comp>
            <County></County>
            <City></City>
            <State></State>
            <Country></Country>
            <ZipCode></ZipCode>
            <Reference></Reference>
        </Address>
    """
    def __init__(
                    self,
                    Street,
                    Number,
                    County,
                    City,
                    State,
                    ZipCode,
                    Country=None,
                    Comp=None,
                    Reference=None
                ):
        self._data = {}
        self._data["Address"] = {
            "Street": Street,
            "Number": Number,
            "County": County,
            "City": City,
            "State": State,
            "ZipCode": ZipCode,
        }

        self.set_no_mandatory_fields_values(locals())

    def get_no_mandatory_fields(self):
        return (
            "Country", "Comp", "Reference"
        )


class Phone(BaseEntity):
    """
    |    Nome   |                  Descrição                   |   Tipo   |  Tamanho   | Obrigatório |
    |===========|==============================================|==========|============|=============|
    | Type      | Tipo de Telefone (Lista de Tipo de Telefone) | Número   |          1 | S           |
    | DDI       | DDI do Telefone                              | Número   |          3 | N           |
    | DDD       | DDD do Telefone                              | Número   |          2 | S           |
    | Number    | Número do Telefone                           | Número   |          9 | S           |
    | Extension | Ramal do Telefone                            | Texto    |         10 | N           |

    - XML representação:
        <Phone>
            <Type></Type>
            <DDI></DDI>
            <DDD></DDD>
            <Number></Number>
            <Extension></Extension>
        </Phone>
    """

    NAO_DEFINIDO = 0
    RESIDENCIAL = 1
    COMERCIAL = 2
    RECADOS = 3
    COBRANCA = 4
    TEMPORARIO = 5
    CELULAR = 6
    TYPES = (
        NAO_DEFINIDO,
        RESIDENCIAL,
        COMERCIAL,
        RECADOS,
        COBRANCA,
        TEMPORARIO,
        CELULAR,
    )

    def __init__(self, Type, DDD, Number, DDI=None, Extension=None):
        self._data = {}
        self._data["Phone"] = {
            "Type": Type,
            "DDD": DDD,
            "Number": Number,
        }

        self.set_no_mandatory_fields_values(locals())

    def get_no_mandatory_fields(self):
        return (
            "DDI", "Extension"
        )
