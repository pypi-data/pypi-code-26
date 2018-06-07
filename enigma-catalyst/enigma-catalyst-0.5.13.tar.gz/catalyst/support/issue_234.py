from catalyst.api import symbol
from catalyst.utils.run_algo import run_algorithm

def initialize(context):
    pass

def handle_data(context, data):
    pass


if __name__ == '__main__':
    performance = run_algorithm(
                                capital_base=1.0,
                                initialize=initialize,
                                handle_data=handle_data,
                                exchange_name='poloniex',
                                data_frequency='minute',
                                quote_currency='btc',
                                algo_namespace='issue_234',
                                simulate_orders=True,
                                live=True)