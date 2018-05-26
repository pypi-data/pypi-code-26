# -*- coding: utf-8 -*-
import os

class Empresa(object):
    def __init__(self, razon_social = None, ruc = None, dir_matriz = None):
        self.razon_social = razon_social
        self.ruc = ruc
        self.dir_matriz = dir_matriz
        self.nombre_comercial = None
        self.dir_establecimiento = None
        self.contribuyente_especial = None
        self.obligado_contabilidad = None
        self.credencial = None #Para firmar archivo xml
        self.password = None #Para firmar archivo xml

class Sujeto(object):
    def __init__(self):
        self.tipo = None
        self.tipo_identificacion = None
        self.razon_social = None
        self.identificacion = None
        self.direccion = None
        self.placa = None
        self.rise = None
        self.telefono = None
        self.email = None

class Comprobante(object):
    id = "comprobante"
    version = "1.0.0"
    moneda = "DOLAR"

    def __init__(self, ambiente = 'pruebas', cod_doc = None, ruta_archivos = None, codigo_numerico = '12345678'):
        # Campos generales
        self.ambiente = ambiente
        self.cod_doc = cod_doc
        self.tipo_emision = None
        self.clave_acceso = None
        self.estab = None
        self.pto_emi = None
        self.secuencial = None
        self.fecha_emision = None
        self.total_sin_impuestos = None
        self.total_descuento = None
        self.total_con_impuestos = []
        self.importe_total = None
        self.pagos = []
        self.info_adicional = []

        # Para facturas
        self.guia_remision = None
        self.propina = None
        self.valor_ret_iva = None
        self.valor_ret_renta = None

        # Para retenciones y nota de débito
        self.periodo_fiscal = None # Solo para retenciones
        self.cod_doc_sustento = None
        self.num_doc_sustento = None
        self.fecha_doc_sustento = None

        # Para guia de remision
        self.direccion_partida = None
        self.fecha_inicio_transporte = None
        self.fecha_fin_transporte = None

        # Para nota de crédito
        self.valor_modificacion = None
        self.motivo = None

        # Sirve para construir la clave de acceso una vez validados todos los datos de la factura
        self.codigo_numerico = codigo_numerico # Un código de 8 números cualquiera

        # La ruta en donde se van a guardar los archivos XML
        self.ruta_archivos = ruta_archivos

class Detalle_Comprobante(object):
    def __init__(self):
        self.codigo_principal = None
        self.codigo_auxiliar = None
        self.descripcion = None
        self.cantidad = None
        self.precio_unitario = None
        self.descuento = None
        self.precio_total_sin_impuesto = None
        self.detalles_adicionales = []
        self.impuestos = []

class Impuesto(object):
    def __init__(self):
        self.codigo = None
        self.codigo_porcentaje = None
        self.tarifa = None
        self.base_imponible = None
        self.descuento_adicional = None
        self.valor = None
        self.porcentaje_retener = None # Para retención únicamente

class Motivo(object):
    def __init__(self, razon = None, valor = None):
        self.razon = razon
        self.valor = valor

class Destinatario(object):
    def __init__(self):
        self.identificacion = None
        self.razon_social = None
        self.direccion = None
        self.motivo_traslado = None
        self.documento_aduanero_unico = None
        self.cod_establecimiento_destino = None
        self.ruta = None
        self.cod_doc_sustento = None
        self.num_doc_sustento = None
        self.num_autorizacion_doc_sustento = None
        self.fecha_doc_sustento = None
        self.detalles = []

class Pago(object):
    def __init__(self):
        self.forma_pago = None
        self.total = None
        self.plazo = None
        self.unidad_tiempo = None

class Detalle_Adicional(object):
    def __init__(self, nombre = None, valor = None):
        self.nombre = nombre
        self.valor = valor