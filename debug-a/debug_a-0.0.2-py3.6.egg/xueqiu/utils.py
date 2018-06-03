# -*- coding: utf-8 -*-


import webbrowser

def make_symbol(code):
    if code.startswith("6"):
        symbol = "SH" + code
    elif code.startswith("3") or code.startswith("0"):
        symbol = "SZ" + code
    else:
        raise ValueError("构造雪球symbol失败，code应当以0/3/6开头")
    return symbol


def open_xueqiu(code):
    """打开code在雪球的页面

    :param code: 股票代码，如 603655
    :return:
    """
    symbol = make_symbol(code)
    url = "https://xueqiu.com/S/" + symbol
    webbrowser.open(url)
