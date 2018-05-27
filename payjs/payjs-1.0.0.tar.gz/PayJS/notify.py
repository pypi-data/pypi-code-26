class PayJSNotify:
    # # <QueryDict: {'attach': '', 'mchid': ['WDQGQD'], 'openid': ['o7LFAwWqr1gw2Hh6Z_Uj1XFgDE0M'], 'out_trade_no': ['84post::6b0a44c787c646b1bb4c5125'], 'payjs_order_id': ['2018052711173900160753334'], 'return_code': ['1'], 'time_end': ['2018-05-27 11:17:50'], 'total_fee': ['1200'], 'transaction_id': ['4200000158201805272545912299'], 'sign': ['0AEC12516865689A1A786E131D4802EA']}>
    def __init__(self, notify_content):
        if type(notify_content) is str:
            from urllib import parse
            notify = dict(parse.parse_qsl(notify_content))
        else:
            notify = dict(notify_content)
