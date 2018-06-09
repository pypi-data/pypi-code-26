from .connection import Connection

class Client():
    ENDPOINT = 'https://coinfalcon.com'

    def __init__(self, key, secret, endpoint = ENDPOINT):
        self.conn = Connection(key, secret, endpoint)

    def accounts(self):
        path = 'user/accounts'

        return self.conn.get(path)

    def create_order(self, order):
        path = 'user/orders'

        return self.conn.post(path, order)

    def cancel_order(self, id):
        path = "user/orders/{}".format(id)

        return self.conn.delete(path)

    def my_orders(self, params = None):
        path = 'user/orders'

        return self.conn.get(path, params)

    def my_trades(self, params = None):
        path = 'user/trades'

        return self.conn.get(path, params)

    def deposit_address(self, currency):
        path = 'account/deposit_address'

        return self.conn.get(path, { 'currency': currency })

    def deposit_history(self, params = None):
        path = 'account/deposits'

        return self.conn.get(path, params)

    def deposit_details(self, id):
        path = 'account/deposit'

        return self.conn.get(path, { 'id': id })

    def create_withdrawal(self, params):
        path = 'account/withdraw'

        return self.conn.post(path, params)

    def withdrawal_details(self, id):
        path = 'account/withdrawal'

        return self.conn.get(path, { 'id': id })

    def withdrawal_history(self, params = None):
        path = 'account/withdrawals'

        return self.conn.get(path, params)

    def cancel_withdrawal(self, id):
        path = "account/withdrawals/{}".format(id)

        return self.conn.delete(path)

    def trades(self, market, params = None):
        path = "markets/{}/trades".format(market)

        return self.conn.get(path, params)

    def orderbook(self, market, params = None):
        path = "markets/{}/orders".format(market)

        return self.conn.get(path, params)

    def fees(self):
        path = 'user/fees'

        return self.conn.get(path)
