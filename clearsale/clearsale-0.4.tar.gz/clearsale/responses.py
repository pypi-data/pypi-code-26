# -*- coding: utf-8 -*-
import xmltodict
from xml.dom.minidom import parseString


class OrderReturn():
    # Pedido foi aprovado automaticamente segundo parâmetros definidos na regra de aprovação automática.
    STATUS_SAIDA_APROVACAO_AUTOMATICA = 'APA'
    # Pedido aprovado manualmente por tomada de decisão de um analista.
    STATUS_SAIDA_APROVACAO_MANUAL = 'APM'
    # Pedido Reprovado sem Suspeita por falta de contato com o cliente dentro do período acordado e/ou políticas restritivas de CPF (Irregular, SUS ou Cancelados).
    STATUS_SAIDA_REPROVADA_SEM_SUSPEITA = 'RPM'
    # Pedido está em fila para análise
    STATUS_SAIDA_ANALISE_MANUAL = 'AMA'
    # Ocorreu um erro na integração do pedido, sendo necessário analisar um possível erro no XML enviado e após a correção reenvia-lo.
    STATUS_SAIDA_ERRO = 'ERR'
    # Pedido importado e não classificado Score pela analisadora (processo que roda o Score de cada pedido).
    STATUS_SAIDA_NOVO = 'NVO'
    # Pedido Suspenso por suspeita de fraude baseado no contato com o “cliente” ou ainda na base ClearSale.
    STATUS_SAIDA_SUSPENSAO_MANUAL = 'SUS'
    # Cancelado por solicitação do cliente ou duplicidade do pedido.
    STATUS_SAIDA_CANCELADO_PELO_CLIENTE = 'CAN'
    # Pedido imputado como Fraude Confirmada por contato com a administradora de cartão e/ou contato com titular do cartão ou CPF do cadastro que desconhecem a compra.
    STATUS_SAIDA_FRAUDE_CONFIRMADA = 'FRD'
    # Pedido Reprovado Automaticamente por algum tipo de Regra de Negócio que necessite aplicá-la (Obs: não usual e não recomendado).
    STATUS_SAIDA_REPROVACAO_AUTOMATICA = 'RPA'
    # Pedido reprovado automaticamente por política estabelecida pelo cliente ou ClearSale.
    STATUS_SAIDA_REPROVACAO_POR_POLITICA = 'RPP'

    STATUS_APPROVED_LIST = (
        STATUS_SAIDA_APROVACAO_AUTOMATICA,
        STATUS_SAIDA_APROVACAO_MANUAL
    )

    STATUS_NOT_APPROVED_LIST = (
        STATUS_SAIDA_REPROVADA_SEM_SUSPEITA,
        STATUS_SAIDA_SUSPENSAO_MANUAL,
        STATUS_SAIDA_CANCELADO_PELO_CLIENTE,
        STATUS_SAIDA_FRAUDE_CONFIRMADA,
        STATUS_SAIDA_REPROVACAO_AUTOMATICA,
        STATUS_SAIDA_REPROVACAO_POR_POLITICA,
    )

    STATUS_WAITING_FOR_APPROVAL_LIST = (
        STATUS_SAIDA_ANALISE_MANUAL,
        STATUS_SAIDA_NOVO,
    )

    STATUS_ERROS_LIST = (
        STATUS_SAIDA_ERRO,
    )

    STATUS_LABEL = {
        STATUS_SAIDA_APROVACAO_AUTOMATICA: u"(Aprovação Automática) – Pedido foi aprovado automaticamente segundo parâmetros definidos na regra de aprovação automática.",
        STATUS_SAIDA_APROVACAO_MANUAL: u"(Aprovação Manual) – Pedido aprovado manualmente por tomada de decisão de um analista.",
        STATUS_SAIDA_REPROVADA_SEM_SUSPEITA: u"(Reprovado Sem Suspeita) – Pedido Reprovado sem Suspeita por falta de contato com o cliente dentro do período acordado e/ou políticas restritivas de CPF (Irregular, SUS ou Cancelados)",
        STATUS_SAIDA_ANALISE_MANUAL: u"(Análise manual) – Pedido está em fila para análise",
        STATUS_SAIDA_ERRO: u"(Erro) - Ocorreu um erro na integração do pedido, sendo necessário analisar um possível erro no XML enviado e após a correção reenvia-lo.",
        STATUS_SAIDA_NOVO: u"(Novo) – Pedido importado e não classificado Score pela analisadora (processo que roda o Score de cada pedido).",
        STATUS_SAIDA_SUSPENSAO_MANUAL: u"(Suspensão Manual) – Pedido Suspenso por suspeita de fraude baseado no contato com o 'cliente' ou ainda na base ClearSale.",
        STATUS_SAIDA_CANCELADO_PELO_CLIENTE: u"(Cancelado pelo Cliente) – Cancelado por solicitação do cliente ou duplicidade do pedido.",
        STATUS_SAIDA_FRAUDE_CONFIRMADA: u"(Fraude Confirmada) – Pedido imputado como Fraude Confirmada por contato com a administradora de cartão e/ou contato com titular do cartão ou CPF do cadastro que desconhecem a compra.",
        STATUS_SAIDA_REPROVACAO_AUTOMATICA: u"(Reprovação Automática) – Pedido Reprovado Automaticamente por algum tipo de Regra de Negócio que necessite aplicá-la (Obs: não usual e não recomendado).",
        STATUS_SAIDA_REPROVACAO_POR_POLITICA: u"(Reprovação Por Política) – Pedido reprovado automaticamente por política estabelecida pelo cliente ou ClearSale.",
    }

    APROVADO = 1
    AGUARDANDO_APROVACAO = 2
    REPROVADO = 3
    ERRO = 4

    STATUS = {}
    STATUS[APROVADO] = u'Aprovado'
    STATUS[AGUARDANDO_APROVACAO] = u'Aguardando aprovação'
    STATUS[REPROVADO] = u'Reprovado'
    STATUS[ERRO] = u'Erro'

    def __init__(self, id, status, score, *args, **kwargs):
        self._id = id
        self._status = status
        self._score = score

    def getID(self):
        return self._id

    def getStatus(self):
        return self._status

    def getScore(self):
        return self._score

    def approved(self):
        return self._status in self.STATUS_APPROVED_LIST

    def not_approved(self):
        return self._status in self.STATUS_NOT_APPROVED_LIST

    def waiting_for_approval(self):
        return self._status in self.STATUS_WAITING_FOR_APPROVAL_LIST

    def has_error(self):
        return self._status in self.STATUS_ERROS_LIST

    def get_analysis(self):
        if self.approved():
            return self.APROVADO
        elif self.not_approved():
            return self.REPROVADO
        elif self.waiting_for_approval():
            return self.AGUARDANDO_APROVACAO
        else:
            return self.ERRO

    def get_analysis_label(self):
        return self.STATUS[self.get_analysis()]

    def get_status_label(self):
        return self.STATUS_LABEL[self._status]


class BaseResponse():
    STATUS_CODE_TRANSACAO_CONCLUIDA = '00'
    STATUS_CODE_USUARIO_INEXISTENTE = '01'
    STATUS_CODE_ERRO_VALIDACAO_XML = '02'
    STATUS_CODE_ERRO_TRANFORMACAO_XML = '03'
    STATUS_CODE_ERRO_INESPERADO = '04'
    STATUS_CODE_PEDIDO_JA_ENVIADO_OU_NAO_ESTA_EM_REANALISE = '05'
    STATUS_CODE_ERRO_PLUGIN_ENTRADA = '06'
    STATUS_CODE_ERRO_PLUGIN_SAIDA = '07'

    def __init__(self, xml, *args, **kwargs):
        self._dict = self._parse_xml_to_dict(xml)
        self._xml = xml

        self._order = None
        self._transaction_id = None
        self._status_code = None
        self._message = None

        # print "### ======================= ###"
        # print self.__class__.__name__
        # print self._xml

        root_node = self._dict["ClearSale"] if "ClearSale" in self._dict else self._dict["PackageStatus"]

        self._orders = []
        if "Orders" in root_node:
            orders = root_node["Orders"]["Order"]
            if isinstance(orders, list):
                for o in orders:
                    if "ID" in o:
                        self._orders.append(OrderReturn(o["ID"], o["Status"], o["Score"]))
            else:
                if "ID" in orders:
                    self._orders.append(OrderReturn(orders["ID"], orders["Status"], orders["Score"]))

        if "StatusCode" in root_node:
            self._transaction_id = root_node["TransactionID"]
            self._status_code = root_node["StatusCode"]
            self._message = root_node["Message"]

    def _parse_xml_to_dict(self, xml):
        xml = xmltodict.parse(xml)
        return xml

    def getTransactionID(self):
        return self._transaction_id

    def getStatusCode(self):
        return self._status_code

    def getMessage(self):
        return self._message

    def getOrders(self):
        return self._orders

    def get_dict(self):
        return self._dict

    def get_xml(self):
        return self._xml

    def get_pretty_xml(self):
        dom = parseString(self.get_xml())
        return dom.toprettyxml()


class OrderStatusResponse(BaseResponse):
    """
    <ClearSale>
        <Orders>
            <Order>
                <ID>TEST-AA11</ID>
                <Status>AMA</Status>
                <Score>22.8200</Score>
            </Order>
        </Orders>
    </ClearSale>
    """


class SendOrdersResponse(BaseResponse):
    """
    <ClearSale>
        <PackageStatus>
            <TransactionID></TransactionID>
            <StatusCode></StatusCode>
            <Message></Message>
            <Orders>
                <Order>
                    <ID></ID>
                    <Status></Status>
                    <Score></Score>
                </Order>
            </Orders>
        </PackageStatus>
    </ClearSale>
    """
