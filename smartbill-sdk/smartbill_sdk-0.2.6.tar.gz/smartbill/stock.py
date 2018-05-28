import requests


class StockSmartBill(object):

    def get_stock(self, date, *args, **kwargs):
        params = {'cif': self.smartbill_ciff,
                  'date': date}
        params.update(kwargs)
        response = requests.get(f"{self.base_url}/stocks", headers=self.headers, params=params)
        return response.json()
