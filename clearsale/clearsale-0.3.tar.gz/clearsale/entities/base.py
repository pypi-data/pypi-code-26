# -*- coding: utf-8 -*-
import json
from xml.dom.minidom import parseString


class BaseEntity(object):

    def serialize(self, root):
        """
        http://www.madchicken.it/2010/06/serialize-a-python-dictionary-to-xml.html
        """
        xml = ''
        for key in root.keys():
            # print "=========="
            # print key
            if isinstance(root[key], dict):
                xml = u'{}<{}>{}</{}>'.format(xml, key, self.serialize(root[key]), key)
            elif isinstance(root[key], list):
                xml = u'{}<{}>'.format(xml, key)
                for item in root[key]:
                    xml = u'{}{}'.format(xml, self.serialize(item))
                xml = u'{}</{}>'.format(xml, key)
            else:
                value = root[key]
                xml = u'{}<{}>{}</{}>'.format(xml, key, value, key)
        return xml

    def get_data(self):
        return self._data

    def get_dict(self):
        data_temp = self._data
        # for k in self._data:
        #     if isinstance(data_temp[k], list):
        #         for i, item in enumerate(data_temp[k]):
        #             if isinstance(item, BaseEntity):
        #                 data_temp[k][i] = item.get_dict()
        #     elif isinstance(data_temp[k], BaseEntity):
        #         data_temp[k] = data_temp[k].get_dict()
        return data_temp

    def get_pretty_dict(self):
        return json.dumps(self.get_dict(), indent=4,)

    def get_xml_root(self):
        return None

    def get_xml(self):
        # root = self.get_xml_root()
        # params = {"root": False,
        #           "attr_type": False}

        # xml = dicttoxml.dicttoxml(self.get_dict(), **params)
        xml = self.serialize(self.get_dict())
        # if root is not None:
        #     xml = "<{0}>{1}</{0}>".format(root, xml)
        return xml

    def get_pretty_xml(self):
        dom = parseString(self.get_xml())
        return dom.toprettyxml()

    def get_no_mandatory_fields(self):
        return []

    def set_no_mandatory_fields_values(self, extra_fields):
        if not self._data:
            self._data = {}

        keys = self._data.keys()
        if keys:
            if isinstance(self._data[keys[0]], dict):
                data_temp = self._data[keys[0]]
            else:
                data_temp = self._data

            for field in self.get_no_mandatory_fields():
                # print field
                value = extra_fields[field]
                # print value
                # print "======================="
                if value is not None:
                    data_temp[field] = value


class BaseCustomer(BaseEntity):
    """
    |      Nome      |                      Descrição                       |             Tipo             |       Tamanho        | Obrigatório |
    |================|======================================================|==============================|======================|=============|
    | ID             | Código do cliente                                    | Texto                        | 50                   | S           |
    | Type           | Pessoa Física ou Jurídica (Lista de Tipos de Pessoa) | Número                       | (1,0)                | S           |
    | LegalDocument1 | CPF ou CNPJ                                          | Texto                        | 100                  | S           |
    | LegalDocument2 | RG ou Inscrição Estadual                             | Texto                        | 100                  | N           |
    | Name           | Nome do cliente                                      | Texto                        | 500                  | S           |
    | BirthDate      | Data de Nascimento                                   | Data                         | (yyyy-mmddThh:mm:ss) | S/N         |
    | Email          | Email                                                | Texto                        | 150                  | N           |
    | Gender         | Sexo (Lista de Tipo de Sexo)                         | Texto                        | 1                    | N           |
    | Address        | Instância de BillingDataAddress                      | BillingDataAddress instância |                      | S           |

    - XML representação:
        <BillingData> ou <ShippingData>
            <ID></ID>
            <Type></Type>
            <LegalDocument1></LegalDocument1>
            <LegalDocument2></LegalDocument2>
            <Name></Name>
            <BirthDate></BirthDate>
            <Email></Email>
            <Gender></Gender>
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
            <Phones>
                <Phone>
                    <Type></Type>
                    <DDI></DDI>
                    <DDD></DDD>
                    <Number></Number>
                    <Extension></Extension>
                </Phone>
            </Phones>
        </BillingData> ou </ShippingData>
    """

    TYPE_PESSOA_FISICA = 1
    TYPE_PESSOA_JURIDICA = 2

    GENDER_MASCULINO = 'M'
    GENDER_FEMININO = 'F'

    def __init__(
                    self,
                    ID,
                    Type,
                    LegalDocument1,
                    Name,
                    Address,
                    BirthDate=None,
                    LegalDocument2=None,
                    Email=None,
                    Gender=None
                ):
        self._data = {
            "ID": ID,
            "Type": Type,
            "LegalDocument1": LegalDocument1,
            "Name": Name,
            "Phones": [],
        }

        self._data.update(Address.get_dict())

        self.set_no_mandatory_fields_values(locals())

    def get_no_mandatory_fields(self):
        return (
            "LegalDocument2", "Email", "Gender", "BirthDate"
        )

    def add_phone(self, Phone):
        self._data[self._data.keys()[0]]["Phones"].append(Phone.get_dict())
