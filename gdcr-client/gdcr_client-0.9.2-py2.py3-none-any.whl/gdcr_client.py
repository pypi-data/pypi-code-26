import requests

class GDCRClient():

    cell_id = None
    universe_base_url = None

    def __init__(self, universe_base_url):
        self.universe_base_url = universe_base_url

    def register_with_universe(self):
        response = requests.get(self.universe_base_url + '/universe/@currentUniverse/register')

        if response.status_code == 200:
            self.cell_id = response.text
        else:
            print('Something has gone wrong!')

        return self.cell_id
