from LServer.utils import Connection
from LServer.utils import DOWNLOAD_PATH
import json
import base64
import os
import functools


J = os.path.join

class Client:

    def __init__(self, my_ip):
        self.ip = "http://localhost:59999" 
        self.my_ip = my_ip
        self.con = None

    def switch(self, ip):
        if ip.startswith("http://"):
            self.ip = ip
        else:
            self.ip = "http://" + ip + ":59999"

    def _action(self, op, data, ip=None, callback=None):
        if not ip:
            ip = self.my_ip
        con = Connection(self.ip, tp='http')
        odata = {
            'req':{
                'op': op,
                'ip': ip,
                }
            }

        odata['req'].update(data)
        res = con.post(json.dumps(odata), callback=callback)
        self.con = con
        if res:
            return res

    def _download(self, name,res):
        if not res:
            return
        r = json.loads(res)
        
        with open(J(DOWNLOAD_PATH, name), 'wb') as fp:
            fp.write(base64.b64decode(r['res'].encode('utf8')))
            print("--------- download ---------")

    def dbshareto(self, ip, file_path):
        if not os.path.exists(file_path):
            return
        self.switch(ip)
        with open(file_path, 'rb') as fp:
            d = base64.b64encode(fp.read()).decode("utf8")
            self.upload(file=file_path,data=d)


    def file(self, ip, file):

        self.switch(ip)
        self.download(file=file, ip=ip, callback=functools.partial(self._download, file))

    def data(self):
        res = self.con.post(json.dumps({'req':{'op':'msg', 'ip':self.my_ip}}))
        return json.loads(res)


    def __getattr__(self, func_name):

        def _rpc(*args, callback=None, **kwargs):
            return self._action(func_name, kwargs, callback=callback)
        return _rpc
