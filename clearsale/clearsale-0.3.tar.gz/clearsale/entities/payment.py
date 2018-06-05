# -*- coding: utf-8 -*-
from .base import BaseEntity


class Payment(BaseEntity):
    """
    |        Nome        |                     Descrição                     |        Tipo       |       Tamanho        | Obrigatório |
    |====================|===================================================|===================|======================|=============|
    | Sequential         | Sequencia de realização do pagamento              | Número            | (1,0)                | N           |
    | Date               | Data do pagamento                                 | Data              | (yyyy-mmddThh:mm:ss) | S           |
    | Amount             | Valor cobrado neste pagamento                     | Número            | (20,4)               | S           |
    | PaymentTypeID      | Tipo de Pagamento (Lista de Tipos de Pagamento)   | Número            | (2,0)                | S           |
    | Address            | instância de Address                              | Address instância |                      | S           |
    | QtyInstallments    | Quantidade de Parcelas                            | Número            | (2,0)                | N           |
    | Interest           | Taxa de Juros                                     | Número            | (4,2)                | N           |
    | InterestValue      | Valor dos Juros                                   | Número            | (20,4)               | N           |
    | CardNumber         | Número do Cartão                                  | Texto             | 200                  | N           |
    | CardBin            | Número do BIN do Cartão                           | Texto             | 6                    | N           |
    | CardEndNumber      | 4 últimos digitos do número de cartão             | Texto             | 4                    | N           |
    | CardType           | Bandeira do Cartão (Lista de Bandeiras de Cartão) | Número            | (1,0)                | N           |
    | CardExpirationDate | Data da Expiração                                 | Texto             | 50                   | N           |
    | Name               | Nome de Cobrança                                  | Texto             | 150                  | N           |
    | LegalDocument      | Documento da Pessoa de Cobrança                   | Texto             | 100                  | N           |
    |                    |                                                   |                   |                      |             |

    - XML representação:
        <Payment>
            <Sequential></Sequential>
            <Date></Date>
            <Amount></Amount>
            <PaymentTypeID></PaymentTypeID>
            <QtyInstallments></QtyInstallments>
            <Interest></Interest>
            <InterestValue></InterestValue>
            <CardNumber></CardNumber>
            <CardBin></CardBin>
            <CardEndNumber></CardEndNumber>
            <CardType></CardType>
            <CardExpirationDate></CardExpirationDate>
            <Name></Name>
            <LegalDocument></LegalDocument>
            <Address>
                <Street></Street>
                <Number></Number>
                <Comp></Comp>
                <County></County>
                <City></City>
                <State></State>
                <Country></Country>
                <ZipCode></ZipCode>
            </Address>
            <Nsu></Nsu>
            <Currency></Currency>
        </Payment>
    """

    CARTAO_CREDITO = 1
    BOLETO_BANCARIO = 2
    DEBITO_BANCARIO = 3
    DEBITO_BANCARIO_DINHEIRO = 4
    DEBITO_BANCARIO_CHEQUE = 5
    TRANSFERENCIA_BANCARIA = 6
    SEDEX_A_COBRAR = 7
    CHEQUE = 8
    DINHEIRO = 9
    FINANCIAMENTO = 10
    FATURA = 11
    CUPOM = 12
    MULTICHEQUE = 13
    OUTROS = 14
    PAYMENT_TYPES_ID = (
        CARTAO_CREDITO,
        BOLETO_BANCARIO,
        DEBITO_BANCARIO,
        DEBITO_BANCARIO_DINHEIRO,
        DEBITO_BANCARIO_CHEQUE,
        TRANSFERENCIA_BANCARIA,
        SEDEX_A_COBRAR,
        CHEQUE,
        DINHEIRO,
        FINANCIAMENTO,
        FATURA,
        CUPOM,
        MULTICHEQUE,
        OUTROS,
    )

    def __init__(
                    self,
                    Date,
                    Amount,
                    PaymentTypeID,
                    Address=None,
                    Sequential=None,
                    QtyInstallments=None,
                    Interest=None,
                    InterestValue=None,
                    CardNumber=None,
                    CardBin=None,
                    CardEndNumber=None,
                    CardType=None,
                    CardExpirationDate=None,
                    Name=None,
                    LegalDocument=None,
                    Nsu=None,
                    Currency=None,
                ):
        self._data = {}
        self._data["Payment"] = {
            "Date": Date,
            "Amount": Amount,
            "PaymentTypeID": PaymentTypeID,
        }

        if Address:
            self._data["Payment"].update(Address.get_dict())

        self.set_no_mandatory_fields_values(locals())

    def get_no_mandatory_fields(self):
        return (
            "Sequential", "QtyInstallments", "Interest", "InterestValue",
            "CardNumber", "CardBin", "CardEndNumber", "CardType",
            "CardExpirationDate", "Name", "LegalDocument", "Nsu", "Currency"
        )
