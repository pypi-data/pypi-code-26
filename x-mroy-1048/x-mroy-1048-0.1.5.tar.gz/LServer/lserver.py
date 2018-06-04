import ipaddress
import sys
import re
import os
import json
import pickle
import base64
import time


from termcolor import cprint, colored

from qlib.file import ensure_path
from qlib.data import Cache, dbobj
from qlib.log import L
from tornado.websocket import WebSocketHandler
from queue import Queue
from functools import partial

import tornado.ioloop
import tornado.web

from termcolor import cprint
from LServer.utils import Connection
from LServer.utils import DOWNLOAD_PATH
from LServer.api import notify
from LServer.settings import HOME
from LServer.settings import TREAT_DESKTOP
from LServer.settings import STATIC_PATH
from LServer.settings import DOWNLOAD_PATH
from LServer.settings import DOCS_PATH
from LServer.settings import DB_PATH
from LServer.settings import PORT
from asynctools.servers import TcpTests
from multiprocessing import Process
from multiprocessing import Queue
import atexit



kill_queue = Queue()
J = os.path.join

def get_our_ip():
    cmd= "ifconfig"
    if sys.platform[:3] == 'win':
        cmd = 'ipconfig'
    ips = re.findall(r'((?:\d{1,3}\.){3}(?:\d{1,3}))', os.popen(cmd).read())
    for i in ips:
    	cprint(i, 'blue')
    while 1:
    	try:
    		ip = int(input("(choose IP [0-%d])" % (len(ips) -1)))
    		return ips[ip],ipaddress.ip_network('.'.join(ips[ip].split(".")[:3]) + ".0/24")
    	except ValueError:
    		cprint("must integer", 'red')
    		continue
    	except IndexError:
    		cprint("must 0-%d" % (len(ips)-1), 'red')
    		continue


MY_IP, OUR_IP = get_our_ip()



def check():
	hosts = [str(i) + ":59999" for i in OUR_IP]
	return [i[0] for i in  TcpTests(hosts) if i[1] < 9999 if i[0] != MY_IP]

def loop_check(queue):
    
    alive_path = J(J(J(os.getenv("HOME"), '.config'), 'treatbook'), 'alive.ips')
    id = os.getpid()
    queue.put(id)
    while 1:
        res = [i+ "\n" for i in check()]
        
        cprint("[up] " + "(" +time.asctime() + ") " + ' '.join([i.split(".")[-1].split(":")[0] for i in res]),'green', end='\r')
        with open(alive_path, 'w') as fp:
            fp.writelines(res)

        time.sleep(7)


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

def set_scan_res(ips):
    MsgBox._alive.add(ips)
    print(MsgBox._alive)




class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.db = self.settings['db']
        self.L = self.settings['L']
        self.shodan = lambda x: None
        if 'shodan' in self.settings:
            self.shodan = self.settings['shodan']
        self.HOME = self.settings['HOME']
        self.msg_box = self.settings['msg_box']
        self.web_path = self.settings['web_path']
        self.DOCS = self.settings['docs_path']

        self.loop = tornado.ioloop.IOLoop.current()

    def get_current_user(self):
        return self.get_cookie('user'),self.get_cookie('passwd')

    def get_current_secure_user(self):
        return (self.get_cookie('user'),self.get_secure_cookie('passwd'))
    def set_current_seccure_user_cookie(self,user,passwd):
        self.set_cookie('user',user)
        self.set_secure_cookie("passwd",passwd)


    def json_arguments(self, key):
        return json.loads(self.request.body)[key]



class SocketHandler(WebSocketHandler):
    """ Web socket """
    clients = set()
    con = dict()
         
    @staticmethod
    def send_to_all(msg, me_id):
        for con in SocketHandler.clients:
            if id(con) == me_id:
                continue
            con.write_message(json.dumps(msg))

    def check_origin(self, origin):
        return True

    @staticmethod
    def send_to_one(msg, id):
        SocketHandler.con[id(self)].write_message(msg)

    def json_reply(self, msg):
        self.write_message(json.dumps(msg))

    def open(self):
        SocketHandler.clients.add(self)
        SocketHandler.con[id(self)] = self
         
    def on_close(self):
        SocketHandler.clients.remove(self)
         
    def on_message(self, msg):
        SocketHandler.send_to_all({
            "text":msg,
            'sendto':True
        }, id(self))


class LoginHandler(BaseHandler):

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow
        args = self.json_arguments("req")
        user = args['user']
        passwd = args['passwd']
        if user + "@" passwd == 'team@work@123':
            return
        self.finish()


class EditorHandler(BaseHandler):

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow
        args = self.json_arguments("req")
        if 'text' in args:
            file = args['file']
            text = args['text']
            with open(J(self.DOCS, file), "w") as fp:
                fp.write(text)
            self.write(json.dumps({"msg":'ok'}))
        else:
            if os.path.exists(J(self.DOCS, args['file'])):
                with open(J(self.DOCS, args['file'])) as fp:
                    d = fp.read()
                    self.write(json.dumps({"msg":'ok', 'text':d}))
            else:
                self.write(json.dumps({"msg":'fali', 'text':''}))
        
        self.finish()



class MainHandler(BaseHandler):
    
    def get(self, **kwargs):
        template = J(self.web_path, "editor.html")
        files = os.listdir(self.DOCS)
        return self.render(template, my_ip=MY_IP, files=files)



    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow
        post_args = self.json_arguments("req")

        op = post_args['op']
        cprint(post_args, 'red')
        res = {'msg': 'null'}
        res['ip'] = MY_IP
        if hasattr(self, op):
            res['res'] = getattr(self, op)(post_args)
            res['msg'] = 'run check'
        
        self.write(json.dumps(res))
        self.finish()

    def scan(self, kwargs):
        res = check()
        MsgBox._alive = res
        return res

    def upload(self, kwargs):
        kwargs = json.loads(kwargs)
        f = kwargs['file']
        d = kwargs['data']
        with open(J(self.HOME, f), 'wb') as fp:
            fp.write(base64.b64decode(d.encode("utf8")))
        return "i got!"

    def msg(self, kwargs):
        msg = self.msg_box.extracts()
        if isinstance(msg, bytes):
            return json.loads(msg)
        return msg

    def reply(self, kwargs):
        self.msg_box.collect(kwargs['ip'], json.dumps(kwargs))
        return 'collect to box'

    def receive(self, data):
        if isinstance(data, bytes):
            data = json.loads(data)
        if 'res' in data:
            self.msg_box.collect(data['ip'], data['res'])
        else:
            self.msg_box.collect(data['ip'], data)

    def ls(self, kwargs):
        files = os.listdir(self.HOME)
        cprint(self.HOME + ":"+' ,'.join(files), 'green')
        tloop = tornado.ioloop.IOLoop.current()
        if 'nobroadcast' in kwargs:
            return files
        else:
            return files

    def download(self,kwargs):
        ip = kwargs['ip']
        if kwargs['file'] in os.listdir(self.HOME):
            if not os.path.isfile(J(self.HOME, kwargs['file'])):
                return None
            with open(J(self.HOME, kwargs['file']), 'rb') as fp:
                d = base64.b64encode(fp.read()).decode("utf8")
            return d


    def _after_download(self, name, res):
        if not res:
            return
        r = json.loads(res)
        if not r['res']:
            return
        
        ip = r['ip']
        with open(J(DOWNLOAD_PATH, name), 'wb') as fp:
            fp.write(base64.b64decode(r['res'].encode('utf8')))
        if sys.platform[:3] == 'dar':
            notify("Download", "finished {}from {}".format(name, ip))
        else:
            print("    --------- download ---------", J(DOWNLOAD_PATH, name), end='\r')
        


    def sendfile(self, kwargs):

        
        ip = kwargs['ip']
        file = kwargs['file']
        from_ip = kwargs['from_ip']
        to_all = kwargs['to_all']
        
        data = json.dumps({
            'req':{
                'op':'download',
                'ip': MY_IP,
                'file': file
            }
        })
        if to_all:
            f = partial(self._after_download, file)
            broadcasts(data, f, self.loop)
        else:
            cprint("-> to download {} : {}".format(from_ip, data),'red')        
            con = Connection("http://{}:59999".format(from_ip), loop=self.loop, tp='http')
            f = partial(self._after_download, file)
            con.post(data, callback=f)

        return "wait result"

    def find(self, kwargs):
        ip = kwargs['ip']
        file = kwargs['file']
        files = []
        for root, ds, fs in os.walk(self.HOME):
            for f in fs:
                if file in f:
                    F = J(root, f).split("TreaShare/", 1)[1]
                    files.append(F)
        if 'nobroadcast' in kwargs:
            if len(files) > 0:
                return files
        else:
            data = json.dumps({
                'req': {
                    'op':'find',
                    'ip':MY_IP,
                    'file':file,
                    'nobroadcast': True
                }})
            broadcasts(data, self.receive, self.loop)
            return files


def broadcasts(data, callback, loop):
    msgbox = MsgBox()
    for ip in msgbox.alive_ips():
        host = "http://" + ip
        con = Connection(host, loop=loop, tp='http')
        con.post(data, callback=callback)

def clean_all():
    while not kill_queue.empty():
        pid = kill_queue.get()
        os.kill(pid, 9)


def run():
    
    
    msg_box = MsgBox()
    def make_app(**kwargs):
        cache = Cache(DB_PATH)

        Settings = {
            'db':cache,
            'L': L,
            'debug':True,
            'msg_box':msg_box,
            'autoreload':True,
            'cookie_secret':'This string can be any thing you want',
            'static_path' : STATIC_PATH,
            'web_path': WEB_PATH,
            'docs_path':DOCS_PATH,
            'HOME' : TREAT_DESKTOP,
        }
        Settings.update(kwargs)
        return tornado.web.Application([
            (r"/", MainHandler),
            (r"/edit", EditorHandler),
            (r"/socketapi", SocketHandler),
        ], share_home, **Settings)
    app = make_app()
    app.listen(int(PORT))
    AnoPro = Process(target=loop_check, args=(kill_queue,))
    AnoPro.start()
    tornado.ioloop.IOLoop.current().start()

atexit.register(clean_all)

if __name__ == "__main__":
    
    run(8888)