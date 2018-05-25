#!/usr/bin/env python3
# -*- coding: utf-8 -*- #

import re
import os
import time
import argparse
import requests


"""
twse official website
http://mis.twse.com.tw

twse API information
https://github.com/Asoul/tsrtc
"""


def alignment(s, space):
  base = len(s)
  count = len(re.findall('[a-zA-Z0-9]', s))
  space = space - (2 * base) + count  # space - ((base - count) * 2) - count
  s = s + (' ' * space)
  return s


def colored(s, color):
  if color == 'green':
    return '\033[1;32m' + s + '\033[m'
  if color == 'red':
    return '\033[1;31m' + s + '\033[m'


class TWSELIB(object):

  def __init__(self):
    self.timestamp = int(time.time() * 1000) + 1000
    self.__req = self.get_cookie()
    pass

  def get_cookie(self):
    api_get_stock_cookie = 'http://mis.twse.com.tw/stock'
    headers = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
      'Content-Type': 'text/html; charset=UTF-8',
      'Accept-Language': 'zh-TW'
    }
    req = requests.session()
    res = req.get(api_get_stock_cookie, headers=headers)
    return req

  def get_stock_key(self, stock_symbol):
    api_get_stock = "http://mis.twse.com.tw/stock/api/getStock.jsp"
    payload = {
      'json': 1,
      '_': self.timestamp,
      'ch': '{}.tw'.format(stock_symbol)
    }
    res = self.__req.get(api_get_stock, params=payload)
    try:
      if res.json()['msgArray'][0]['key']:
        return res.json()['msgArray'][0]['key']
    except IndexError as err:
      print("Index error: {}".format(err))
      return ''

  def get_stock_info(self, stock_keys):
    api_get_stock_info = "http://mis.twse.com.tw/stock/api/getStockInfo.jsp"
    payload = {
      'json': 1,
      '_': self.timestamp,
      'delay': 0,
      'ex_ch': '%7C'.join(stock_keys)
    }
    res = self.__req.get(api_get_stock_info, params=payload)
    try:
      if res.json()['msgArray']:
        return res.json()['msgArray']
    except KeyError as err:
      print("Key error: {}".format(err))
      return []


def print2terminal(stock_infos):
  if stock_infos:
    print('\n代號  商品          成交   漲跌    幅度    單量    總量   最高   最低   開盤   昨收')
    for stock in stock_infos:
      change = float(stock['z']) - float(stock['y'])
      change_p = change / float(stock['y'])
      stock_name = alignment(stock['n'], 11)
      stock_price = colored('{:>6}'.format(stock['z']), 'red') if change >= 0 else colored('{:>6}'.format(stock['z']), 'green')
      stock_change = colored('{:>+6.2f}'.format(change), 'red') if change >= 0 else colored('{:>+6.2f}'.format(change), 'green')
      stock_change_p = colored('{:>+7.2%}'.format(change_p), 'red') if change >= 0 else colored('{:>+7.2%}'.format(change_p), 'green')
      stock_change_high = colored('{:>6}'.format(stock['h']), 'red') if float(stock['h']) - float(stock['y']) >= 0 else colored('{:>6}'.format(stock['h']), 'green')
      stock_change_low = colored('{:>6}'.format(stock['l']), 'red') if float(stock['l']) - float(stock['y']) >= 0 else colored('{:>6}'.format(stock['l']), 'green')
      stock_change_origin = colored('{:>6}'.format(stock['o']), 'red') if float(stock['l']) - float(stock['y']) >= 0 else colored('{:>6}'.format(stock['o']), 'green')
      print("{:<5} {} {} {} {} {:>7,} {:>7,} {} {} {:>6} {:>6}".format(stock['c'], stock_name, stock_price, stock_change, stock_change_p, int(stock['tv']), int(stock['v']), stock_change_high, stock_change_low, stock_change_origin, stock['y']))
    else:
      print('\n資料時間: {} {}'.format(stock['d'], stock['t']))


def main():
  stock_keys = []
  stock_symbols = []
  stock_interval = None
  stock_config = os.path.expanduser('~/.config/twsecli/config')

  # init config
  if not os.path.isfile(stock_config):
    os.makedirs(os.path.dirname(stock_config))
    with open(stock_config, 'w', encoding='utf-8') as outf:
      outf.write('0050\n')
      outf.write('0056\n')

  # argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("symbol", nargs="*", help="stock symbol", type=int)
  parser.add_argument("-n", "--interval", metavar="", help="seconds to wait between updates, minimum 60s", type=int)
  parser.add_argument("-c", "--config", metavar="", help="stock symbol config, default path ~/.config/twsecli/config")
  argv = parser.parse_args()
  if argv.config:
    stock_config = os.path.expanduser(argv.config)
  if len(argv.symbol) == 0:
    try:
      print('讀取設定檔: {}'.format(stock_config))
      with open(stock_config, 'r', encoding='utf-8') as inf:
        for line in inf:
          if line.strip():
            stock_symbols.append(line.strip())
    except OSError as err:
      print('OS error: {}'.format(err))
      return
  else:
    stock_symbols = argv.symbol
  if argv.interval:
    stock_interval = 60 if argv.interval < 60 else argv.interval

  # create object
  twse_lib = TWSELIB()
  for stock_symbol in stock_symbols:
    key = twse_lib.get_stock_key(stock_symbol)
    stock_keys.append(key)
  while True:
    stock_infos = twse_lib.get_stock_info(stock_keys)
    if stock_infos:
      if stock_interval:
        os.system('clear')
      print2terminal(stock_infos)
      if stock_interval:
        try:
          print('資料更新頻率: {}s'.format(stock_interval))
          time.sleep(argv.interval)
        except KeyboardInterrupt:
          break
      else:
        break
    else:
      break

  # gc object
  del twse_lib
  pass


if __name__ == '__main__':
  main()
