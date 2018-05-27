import requests


class ConfigSmartBill(object):

    def get_tax(self):
        response = requests.get(f"{self.base_url}/tax", headers=self.headers, params=self.parrams)
        return response.json()

    def get_series(self):
        response = requests.get(f"{self.base_url}/series", headers=self.headers, params=self.parrams)
        return response.json()
