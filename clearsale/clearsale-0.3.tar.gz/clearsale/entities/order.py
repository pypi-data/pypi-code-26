# -*- coding: utf-8 -*-
from .base import BaseEntity


class Orders(BaseEntity):
    def __init__(self, *args, **kwargs):
        self._data = {"Orders": []}

    def add_order(self, order):
        self._data["Orders"].append(order.get_dict())


class Order(BaseEntity):
    """
    |        Nome          |                                    Descrição                                       |          Tipo             | Tamanho   |                                             Obrigatório                                                |
    | ==================== | ================================================================================== | ========================  | ========= | ====================================================================================================== |
    | ID                   | Código do pedido                                                                   | String                    | 50        | S                                                                                                      |
    | FingerPrint          | Instância de FingerPrint                                                           | FingerPrint instância     |           | S                                                                                                      |
    | Date                 | Data do pedido                                                                     | Data (yyyy-mmddThh:mm:ss) |           | S                                                                                                      |
    | Email                | Email do pedido                                                                    | Texto                     | 150       | S                                                                                                      |
    | TotalItems           | Valor do Itens                                                                     | Decimal                   | (20,4)    | S                                                                                                      |
    | TotalOrder           | Valor do Itens                                                                     | Decimal                   | (20,4)    | S                                                                                                      |
    | QtyInstallments      | Quantidade de Parcelas                                                             | Número                    | (1,0)     | S                                                                                                      |
    | IP                   | IP do Pedido                                                                       | Texto                     | (50)      | S                                                                                                      |
    | Status               | Status do Pedido (na entrada) (Lista de status (de entrada)                        | Número                    | (1,0)     | N (se não for enviada a tag o pedido entrará como novo )                                               |
    | Origin               | Origem do Pedido                                                                   | Texto                     | 150       | S                                                                                                      |
    | ListTypeID           | ID do tipo de lista (Lista de Tipos de Lista)                                      | Número                    | (1,0)     | S                                                                                                      |
    | ListID               | ID da lista na loja                                                                | Texto                     | 200       | S                                                                                                      |
    | BillingData          | instância de BilingData                                                            | BillingData instância     |           | S                                                                                                      |
    | ShippingData         | instância de ShoppinData                                                           | ShippingData instância    |           | S                                                                                                      |
    | B2B_B2C=3            | Tipo do ecommerce                                                                  | Texto                     | 3         | N                                                                                                      |
    | ShippingPrice=""     | Valor do Frete                                                                     | Decimal                   | (20,4)    | N                                                                                                      |
    | DeliveryTimeCD=""    | Prazo de Entrega                                                                   | Texto                     | 50        | N                                                                                                      |
    | QtyItems=""          | Quantidade de Itens                                                                | Número                    | (1,0)     | N                                                                                                      |
    | QtyPaymentTypes=""   | Quantidade de Pagamentos                                                           | Número                    | (1,0)     | N                                                                                                      |
    | ShippingType=""      |                                                                                    |                           |           |                                                                                                        |
    | Gift=""              | Identifica se o pedido é presente                                                  | Número                    | (1,0)     | N                                                                                                      |
    | GiftMessage=""       | Mensagem de Presente   N                                                           | Texto                     | 8000      | N                                                                                                      |
    | Obs="",              | Observação do pedido                                                               | Texto                     | 8000      | N                                                                                                      |
    | Reanalise=0          | Marcação que indica se o pedido será reanalisado ou não (1 caso for, 0 caso não)   | Número                    | (1,0)     | N                                                                                                      |
    | Country="",          | Nome do País                                                                       | Texto                     | 50        | N(somente para pedidos de análise internacional)                                                       |
    | Nationality="",      | Nome da Nacionalidade                                                              | Texto                     | 50        | N(somente para pedidos de análise internacional)                                                       |
    | Product=4,           | ID do produto (Lista de Produtos)                                                  | Número                    | 4         | N(somente para pedidos de análise internacional ou clientes que utilizam mais produtos da ClearSale)   |
    |                      |                                                                                    |                           |           |                                                                                                        |

    - XML representação:
        <Order>
            <ID></ID>
            <FingerPrint>
                <SessionID></SessionID>
            </FingerPrint>
            <Date></Date>
            <Email></Email>
            <B2B_B2C></B2B_B2C>
            <ShippingPrice></ShippingPrice>
            <TotalItems></TotalItems>
            <TotalOrder></TotalOrder>
            <QtyInstallments></QtyInstallments>
            <DeliveryTimeCD></DeliveryTimeCD>
            <QtyItems></QtyItems>
            <QtyPaymentTypes></QtyPaymentTypes>
            <IP></IP>
            <ShippingType></ShippingType>
            <Gift></Gift>
            <GiftMessage></GiftMessage>
            <Obs></Obs>
            <Status></Status>
            <Reanalise></Reanalise>
            <Origin></Origin>
            <Country></Country>
            <Nationality></Nationality>
            <Product></Product>
            <ListTypeID></ListTypeID>
            <ListID></ListID>
            <BillingData>
                ...
            </BillingData>
            <ShippingData>
                ...
            </ShippingData>
            <Payments>
                <Payment>
                    ...
                </Payment>
            </Payments>
            <Items>
                <Item>
                    ...
                 </Item>
            </Items>
        </Order>
    """

    DATE_TIME_FORMAT = 'Y-m-d\TH:i:s'

    # B2B_B2C
    ECOMMERCE_B2B = 'b2b'
    ECOMMERCE_B2C = 'b2c'

    # Status
    STATUS_NOVO = 0
    STATUS_APROVADO = 9
    STATUS_CANCELADO = 41
    STATUS_REPROVADO = 45

    # Product
    PRODUCT_A_CLEAR_SALE = 1
    PRODUCT_M_CLEAR_SALE = 2
    PRODUCT_T_CLEAR_SALE = 3
    PRODUCT_TG_CLEAR_SALE = 4
    PRODUCT_TH_CLEAR_SALE = 5
    PRODUCT_TG_LIGHT_CLEAR_SALE = 6
    PRODUCT_TG_FULL_CLEAR_SALE = 7
    PRODUCT_T_MONITORADO = 8
    PRODUCT_SCORE_DE_FRAUDE = 9
    PRODUCT_CLEAR_ID = 10
    PRODUCT_ANALISE_INTERNACIONAL = 11

    # ListTypeID
    LIST_TYPE_NAO_CADASTRADA = 1
    LIST_TYPE_CHA_DE_BEBE = 2
    LIST_TYPE_CASAMENTO = 3
    LIST_TYPE_DESEJOS = 4
    LIST_TYPE_ANIVERSARIO = 5
    LIST_TYPE_CHA_BAR_OU_CHA_PANELA = 6

    def __init__(
                    self,
                    ID,
                    FingerPrint,
                    Date,
                    Email,
                    TotalItems,
                    TotalOrder,
                    QtyInstallments,
                    IP,
                    BillingData,
                    ShippingData,
                    Origin=None,
                    ListTypeID=None,
                    ListID=None,
                    Status=None,
                    B2B_B2C=None,
                    ShippingPrice=None,
                    DeliveryTimeCD=None,
                    QtyItems=None,
                    QtyPaymentTypes=None,
                    ShippingType=None,
                    Gift=None,
                    GiftMessage=None,
                    Obs=None,
                    Reanalise=None,
                    Country=None,
                    Nationality=None,
                    Product=None,
                ):

        self._data = {}
        self._data["Order"] = {
            "ID": ID,
            "Date": Date,
            "Email": Email,
            "TotalItems": TotalItems,
            "TotalOrder": TotalOrder,
            "QtyInstallments": QtyInstallments,
            "IP": IP,
            "Origin": Origin or "WEB",
            "Payments": [],
            "Items": [],
        }

        self._data["Order"].update(FingerPrint.get_dict())
        self._data["Order"].update(BillingData.get_dict())
        self._data["Order"].update(ShippingData.get_dict())

        self.set_no_mandatory_fields_values(locals())

    def get_no_mandatory_fields(self):
        return (
            "B2B_B2C", "ShippingPrice", "DeliveryTimeCD", "QtyItems", "QtyPaymentTypes",
            "ShippingType", "Gift", "GiftMessage", "Obs", "Reanalise", "Country",
            "Nationality", "Product", "Status", "ListTypeID", "ListID",
        )

    def add_payment(self, Payment):
        self._data["Order"]["Payments"].append(Payment.get_dict())

    def add_item(self, Item):
        self._data["Order"]["Items"].append(Item.get_dict())
