import pybithumb
import csv

keys = next(csv.reader(open("keys.csv")))
bithumb = pybithumb.Bithumb(keys[0].strip(), keys[1].strip())

# ----------------------------------------------------------------------------------------------
# 잔고 조회
# ----------------------------------------------------------------------------------------------
for coin in pybithumb.get_tickers():
    print(coin, bithumb.get_balance())

