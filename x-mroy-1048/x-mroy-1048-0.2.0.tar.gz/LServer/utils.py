import aiohttp
from asynctools.servers import Connection as _Connection
import threading
import time
import socket
import requests
import sys
import os
import tornado.ioloop
import webbrowser

from functools import partial
from multiprocessing.pool import ThreadPool

from termcolor import cprint

_workers = ThreadPool(10)

J = os.path.join


class MsgBox:
    _msg = {}
    _alive = set()

    def collect(self, ip, data):
        MsgBox._msg[ip] = data

    def extract(self, ip):
        return MsgBox._msg[ip]

    def extracts(self):
        return MsgBox._msg

    def alive_ips(self):
        alive_path = J(J(J(os.getenv("HOME"), '.config'), 'treatbook'), 'alive.ips')
        with open(alive_path) as fp:
            return [i.strip() for i in fp.readlines()]

def run_background(func, callback, loop=None, args=(), kwds={}):
    if not loop:
        loop = tornado.ioloop.IOLoop.instance()
    def _callback(result):
        # print(callback,result)
        # loop.add_callback(partial(callback, result))
        if not callback:
            cprint("[?] nothing back", 'yellow')
            return
        callback(result)
    _workers.apply_async(func, args, kwds, _callback)


def start_browser(url):
    cprint("[+] Opening browser : {}".format(url))
    webbrowser.open(url)



class _WConnection:

    def __init__(self, url, loop=None,tp='http'):
        self.url = url
        self.loop = loop

    def _post(self, data, **kwargs):

        res = requests.post(self.url, data=data, **kwargs)
        if res.status_code == 200:
            return res.content

    def post(self, data, callback, **kwargs):
        run_background(self._post, callback, loop=self.loop, args=(data,), kwds=kwargs)

if sys.platform[:3] != 'win':
    Connection = _Connection
    # Connection = _WConnection
else:
    Connection = _WConnection




class Background(threading.Thread):

    def __init__(self, func, *ags, args=(),kwargs={}, callback=None, repeat=7,loop=None, **kwgs):
        super().__init__(*ags, **kwgs)
        self.f = func
        self.args = args
        self.kwargs = kwargs
        self.repeat = repeat
        self.loop = loop
        self.callback = callback

    def run(self):
        fun = self.f
        args = self.args
        kwargs = self.kwargs
        repeat = self.repeat
        callback = self.callback
        while 1:
            time.sleep(repeat)
            res = fun(*args, **kwargs)
            if self.loop:
                self.loop.add_callback(functools.partial(callback, res))
            print(time.asctime(),' B')
            

def tcp_echo_client(hosts, loop, callback):
    for host in hosts:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        ip = str(host)
        port = 59999
        try:
            s.connect((ip, int(port)))
        except socket.error:
            return
        except socket.timeout:
            return
        loop.add_callback(functools.partial(callback, host))

# def echo_all(hosts, loop, callback):
#   c = 0
#   ts = []
#   while hosts:
#       h = hosts.pop()
        
#       t = Thread(target=tcp_echo_client, args=(h, loop, callback,))
#       t.start()
#       ts.append(t)
        
#       if len(ts) > 30:
#           while 1:
#               time.sleep(1)
#               ds = []
#               for T in ts:
#                   if not T.is_alive():
#                       ds.append(T)
#               if not ds:
#                   continue
#               for d in ds:
#                   ts.remove(d)
#               break




async def asyn_tcp_echo_client(num, host, loop):
    h, p = host.split(":")
    try:
        st = time.time()
        conner = asyncio.open_connection(h, int(p), loop=loop)
        reader, writer = await asyncio.wait_for(conner, timeout=7)
        et = time.time() -st
        # print('Close the socket')
        writer.close()
        return host,et

    except asyncio.TimeoutError:
        return host,9999
    except socket.error as e:
        # traceback.print_stack()
        return host,9999
    # print('Send: %r' % message)
    # writer.write(message.encode())

    # data = yield from reader.read(100)
    # print('Received: %r' % data.decode())


async def _tcp_test(hosts, loop):
    
    task = [asyn_tcp_echo_client(i, host, loop) for i, host in enumerate(hosts)]
    return await asyncio.gather(*task)






# async def _post(self, url, data, loop, proxy=None):
#   connector = aiohttp.ProxyConnector(proxy=proxy)
#   session =  aiohttp.ClientSession(loop=self.loop, connector=conn, request_class=ProxyClientRequest)
#     async with session.post(url, **kwargs) as response:
#       log.info('post : {}'.format(url))
#         if not response.status == 200:
#             log.error("Error: %d" % response.status)
#             await response.release()
#         else:
#             try:
#                 return await response.text()
#             except Exception:
#                 return await response.release()


#   