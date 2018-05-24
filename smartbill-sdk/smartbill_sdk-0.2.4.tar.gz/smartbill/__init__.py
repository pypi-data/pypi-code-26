from .authenticate import AuthenticateMixin
from .invoice import InvoiceSmartBill
from .stock import StockSmartBill
from .config import ConfigSmartBill


class SmartBill(InvoiceSmartBill, StockSmartBill, AuthenticateMixin, ConfigSmartBill,):
    base_url = 'https://ws.smartbill.ro:8183/SBORO/api'

    def __init__(self, smartbill_user, smartbill_token, smartbill_ciff,
                 currency='RON', language='RO', save_to_db=False, use_stock=False):
        self.smartbill_user = smartbill_user
        self.smartbill_token = smartbill_token
        self.smartbill_ciff = smartbill_ciff
        self.parrams = {'cif': self.smartbill_ciff}
        self.currency = currency
        self.language = language
        self.save_to_db = save_to_db
        self.use_stock = use_stock
        super().__init__()
