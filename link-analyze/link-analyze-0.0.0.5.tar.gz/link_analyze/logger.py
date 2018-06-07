# --*--coding: utf-8 --*--

import os
import time

REQ_URLS_FILE = open('link-analyze-log.txt', 'a')

def logger(message, write=True):
    w = '\033[0m'
    g = '\033[32m'
    message = str(message)
    cur_time = time.strftime('%a, %d %b %Y %H:%M:%S %z: ')
    # write log message to log file if `write == true`
    if write:
        REQ_URLS_FILE.write(''.join([str(cur_time), message, '\n']))
        REQ_URLS_FILE.flush()
        os.fsync(REQ_URLS_FILE.fileno())
    print(''.join([g, str(cur_time), w, message]))
