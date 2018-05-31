import urllib.request
import pygal
from pygal.style import DarkGreenBlueStyle
import json
import os
import webbrowser

API_KEY = '0ccea2063d54ff0b3f381c4b7d271d54'


def main():
    # url with Bitcoin USD value in JSON format
    url = "https://api.coindesk.com/v1/bpi/historical/close.json"

    bitcoin_data_request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    bitcoin_data = urllib.request.urlopen(bitcoin_data_request)

    bitcoin_data_in_bytes = bitcoin_data.read()

    bitcoin_dict = json.loads(bitcoin_data_in_bytes)

    bitcoin_dict_cleaned = bitcoin_dict["bpi"]

    # url with current exchange values in JSON format
    url_2 = "http://data.fixer.io/api/latest?access_key=0ccea2063d54ff0b3f381c4b7d271d54"

    exchange_rates_data_request = urllib.request.Request(url_2, headers={'User-Agent': 'Mozilla/5.0'})

    exchange_rates_data = urllib.request.urlopen(exchange_rates_data_request)

    exchange_rates_data_in_bytes = exchange_rates_data.read()

    exchange_rates_dict = json.loads(exchange_rates_data_in_bytes)

    exchange_rates_dict_cleaned = exchange_rates_dict["rates"]

    exchange_rates_USD_to_EUR_ratio = exchange_rates_dict_cleaned["USD"]

    dates = []
    closing_prices_in_usd = []
    closing_prices_in_eur = []

    for key, value in bitcoin_dict_cleaned.items():
        dates.append(key)
        closing_prices_in_usd.append(value)

    for value_in_usd in closing_prices_in_usd:
        value_in_eur = value_in_usd / exchange_rates_USD_to_EUR_ratio
        closing_prices_in_eur.append(value_in_eur)

    line_chart = pygal.Line(style=DarkGreenBlueStyle)
    line_chart.title = "Bitcoin value graph"
    line_chart.x_labels = dates
    line_chart.add("Value in USD", closing_prices_in_usd)
    line_chart.add("Value in EUR", closing_prices_in_eur)

    cwd = os.getcwd()
    line_chart.render_to_file(f"{cwd}/bitcoin-value-graph.svg")
    webbrowser.open(f"{cwd}/bitcoin-value-graph.svg")


if __name__ == '__main__':
    main()
