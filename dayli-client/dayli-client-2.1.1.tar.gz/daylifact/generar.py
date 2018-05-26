# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ETXML
from daylifact.utils import SCHEMAS
import os
import sys
from daylifact.logica import Crear_XML
import requests
import base64
from requests.exceptions import ConnectionError

try:
    from lxml import etree
    from lxml.etree import fromstring, DocumentInvalid
except ImportError:
    raise Exception('Instalar librería lxml')

class DocumentXML(object):
    _schema = False
    document = False
    SriServiceObj = False

    @classmethod
    def __init__(self, document, type='out_invoice'):
        """
        document: XML representation
        type: determinate schema
        """
        parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
        self.document = fromstring(document, parser=parser)
        self.type_document = type
        self._schema = SCHEMAS[self.type_document]
        self.signed_document = False

    @classmethod
    def validate_xml(self):
        """
        Validar esquema XML
        """
        file_path = os.path.join(os.path.dirname(__file__), self._schema)
        schema_file = open(file_path)
        xmlschema_doc = etree.parse(schema_file)
        xmlschema = etree.XMLSchema(xmlschema_doc)

        try:
            xmlschema.assertValid(self.document)
            return True
        except DocumentInvalid as e:
            print e
            return False

def Generar_XML(empresa, sujeto, documento, detalle_documento):
    dic_autorizacion = {'fecha': None, 'numero': None}

    try:
        #Verificar que exista la ruta para los archivos generados
        RUTA_ARCHIVOS = documento.ruta_archivos

        if not os.path.exists(RUTA_ARCHIVOS):
            os.makedirs(RUTA_ARCHIVOS)

        # Enviar las entidades 'Empresa', 'Cliente o Proveedor', 'Documento (Factura, Retencion....)' y la lista de Entidades '(Detalle_Factura, impuests de retencion....)'
        estado = Crear_XML(empresa, sujeto, documento, detalle_documento)

        if estado[0]:
            rootWrite = estado[1]
            ein = rootWrite.getroot()
            einvoice = ETXML.tostring(ein, encoding="utf8", method='xml')

            #Validar xml con los archivos xsd
            validar_xsd = DocumentXML(einvoice, documento.cod_doc)

            if not validar_xsd.validate_xml():
                return {'data': {'result': False, 'message': 'El XML no ha pasado la validación', 'autorizacion': dic_autorizacion }}

            # Crear la carpeta generados, en caso de no existir
            directorio_generados = os.path.join(RUTA_ARCHIVOS + '/generados')
            directorio_autorizados = os.path.join(RUTA_ARCHIVOS + '/autorizados')
            directorio_firmados = os.path.join(RUTA_ARCHIVOS + '/firmados')

            if not os.path.exists(directorio_generados):
                os.makedirs(directorio_generados)

            if not os.path.exists(directorio_autorizados):
                os.makedirs(directorio_autorizados)

            if not os.path.exists(directorio_firmados):
                os.makedirs(directorio_firmados)

            # Envio de Informacion
            r = requests.post('http://104.236.239.181:9000/api/firmar/', data={'credential': empresa.credencial,
                                                                     'file': base64.b64encode(einvoice),
                                                                     'password': empresa.password})
            if (r.status_code != 200):
                return {'data': {'result': False, 'message': 'Servicio DAYLIFACT no disponible.', 'autorizacion': dic_autorizacion }}

            __json_result = r.json()

            rootWrite.write(os.path.join(RUTA_ARCHIVOS + '/generados', documento.clave_acceso + '.xml'),encoding='utf8', xml_declaration=True)

            if __json_result['result']:
                firmado = __json_result['firmado']
                autorizado = __json_result['autorizado']['file']
                fecha_autorizacion = __json_result['autorizado']['fecha']
                numero_autorizacion = __json_result['autorizado']['autorizacion']

                # Guardar archivos firmados y autorizados
                if firmado and autorizado:
                    root_str = ETXML.fromstring(autorizado.encode("utf8"))
                    root_str_Write = ETXML.ElementTree(root_str)
                    root_str_Write.write(os.path.join(RUTA_ARCHIVOS + '/autorizados', documento.clave_acceso + '.xml'), encoding='utf8', xml_declaration=True)

                    root_str2 = ETXML.fromstring(firmado.encode("utf8"))
                    root_str_Write2 = ETXML.ElementTree(root_str2)
                    root_str_Write2.write(os.path.join(RUTA_ARCHIVOS + '/firmados', documento.clave_acceso + '.xml'), encoding='utf8', xml_declaration=True)

                    dic_autorizacion = {'fecha': fecha_autorizacion, 'numero': numero_autorizacion }

            return {'data': {'result': __json_result['result'], 'message': __json_result['message'],
                             'autorizacion': dic_autorizacion}}  # Errores
        else:
            return {'data': {'result': False, 'message': estado[1]['result'], 'autorizacion': dic_autorizacion}}
    except ConnectionError:
        return {'data': {'result': False, 'message': 'Se produjo un error durante el intento de conexión ya que la parte conectada no respondió adecuadamente tras un periodo de'
                                                     ' tiempo, o bien se produjo un error en la conexión establecida ya que el host conectado no ha podido responder',
                         'autorizacion': dic_autorizacion }}
    except Exception as e:
        print e
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_details = {
            'line': exc_traceback.tb_lineno,
            'name': exc_traceback.tb_frame.f_code.co_name,
            'type': exc_type.__name__,
            'message': exc_value.message
        }
        print traceback_details
        return {'data': {'result': False, 'message': traceback_details['message'], 'autorizacion': dic_autorizacion }}