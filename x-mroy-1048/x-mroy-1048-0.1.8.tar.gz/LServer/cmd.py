import cmd, sys
import os
import re
import json
import base64
import time
from functools import partial

from LServer.llocal import Client
from LServer.lserver import MsgBox, MY_IP
from LServer.settings import HOME
from LServer.settings import DB_PATH

from qlib.data import Cache, dbobj
from termcolor import cprint, colored


def _wcprint(*args, **kwargs):
    print(*args,**kwargs)

def _wcolored(*args, **kwargs):
    return ' '.join(args)

if sys.platform[:3] == 'win':
    cprint = _wcprint
    colored = _wcolored


class RShell(cmd.Cmd):

    def __init__(self):
        super().__init__()
        self.prompt = colored("=> ", 'red')
        self.c = Client("localhost")
        self.db = Cache(DB_PATH)
        self.hosts = set()
        self.cd_ip =  MY_IP
        self.my_ip = MY_IP
        self.tmp_find = {}
        self.local_find = {}
        self.local_search = {}
        self.tmp_search = {}
        self.do_scan(None)

    def do_exit(self, args):
        return True

    def _pre_find_files(self, files, setname='tmp_find'):
        t = json.loads(files)['res']
        if isinstance(t, list):
            setattr(self, setname, t)
            # self.tmp_find = t
        else:
            m = None
            for k in t:
            # if '127.0.0.1' in t:
                m = t[k]
                if not isinstance(m, list):
                    if not m or not 'res' in m:
                        # cprint('[!] no data')
                        continue         
                    m = m['res']

                if isinstance(m, list):
                    getattr(self, setname).update({k:m})
            
            

    def do_find(self, args):
        f = partial(self._pre_find_files, setname='local_find')
        self.c.find(file=args)
        time.sleep(1)
        cprint("[!] get data use show", 'yellow' )
        self.c.msg(callback=self._pre_find_files)

    def do_cd(self, args):
        self.cd_ip =  args
        self.c.switch(args.strip())

    def complete_cd(self, text, line, begidx, endidx):
        e = [ i.split(":")[0] for i in self.hosts]
        w = []
        for i in e:
            if text in i:
                w.append(i)
        return w

    def do_sendfile(self, args):
        self.c.sendfile(file=args, ip=self.cd_ip, to_all=False, from_ip=MY_IP)
        # cprint()        
    def complete_sendfile(self, text, line, begidx, endidx):
        pass

    def do_download(self, args):
        self.c.file(self.cd_ip, args)
        # cprint('[Download]', 'green')

    def complete_download(self, text, line, begidx, endidx):
        fs = []
        for f in self.tmp_find[self.cd_ip]:
            if text in f:
                fs.append(f)
        return fs

    def DP(self, args):
        # print("hehe")
        if isinstance(args, bytes):
            cprint("[+] {}\n{}".format(json.loads(args)['res'], self.prompt), 'green', end='')
        else:
            cprint(args, 'red')

    def do_ls(self, args):
        res = self.c.ls(callback=self.DP)
        

    def do_scan(self, args):
        self.hosts = MsgBox().alive_ips()
        for i in self.hosts:
            cprint(colored("[up] ", 'green') + i, 'blue')

    def do_show(self, args):
        
        for k in ['hosts', 'cd_ip' ,'ObjCls', 'tmp_find']:
            if hasattr(self, k):
                print(colored('[+]','green'), k,'->',getattr(self,k))

    def do_query(self, args):
        if not hasattr(self, "ObjCls"):
            cprint("[!] not set ObjCls")
            return
        if '=' in args:
            k,v = args.split("=",1)
        o = self.c.query_one(self.ObjCls,**{k:v})
        if o:
            keys = list(o.get_fields())
            for k in keys:
                v = o[k]
                cprint("{} [+] {} -> {}".format(self.ObjCls.__name__,k, v), 'green')

    def do_dbshareto(self, args):
        self.db.export_xlsx("/tmp/db.xlsx")
        self.c.shareto(args, "/tmp/db.xlsx")
        cprint("[+] share db to {}".format(args), 'green')
    
    def do_set(self, args):
        if not hasattr(self, 'ObjCls'):
            cprint('[!] not set Obj : use []', 'red')
        else:
            k,v = None, None
            try:
                k, v = args.split()
            except ValueError:
                cprint("[!] must 'k v' ", 'red')
                return
            if not hasattr(self, 'tmp_data'):
                self.tmp_data = {}
            self.tmp_data[k] = v
            cprint("[+] {} -> {}".format(k, v), 'green')

    def do_save(self, args):
        if not hasattr(self, 'ObjCls'):
            cprint('[!] not set Obj : use []', 'red')
            return
        if not hasattr(self, 'tmp_data'):
            cprint('[!] not set data: set k v', 'red')
            return

        O = self.ObjCls(**self.tmp_data)
        try:
            O.save(self.db)
        except:
            ObjCls_bak = type(self.ObjCls.__name__ +"_bak", (dbobj,), {})
            O2 = ObjCls_bak(**self.tmp_data)
            cprint("[?] use backup Dbobj: {}".format(ObjCls_bak.__name__), 'yellow')
            try:
                O2.save(self.db)
            except:
                cprint("[!] DB error ", 'red')

    def complete_use(self, text, line, begidx, endidx):
        tbs = self.db.ls()
        q =[]
        for i in tbs:
            if text in i:
                q.append(i)
        return q



    def do_use(self, args):
        if ' ' not in args and re.match(r'\w+', args):
            self.ObjCls = type(args.strip(), (dbobj,), {})
            cprint("[+] use dbobj: %s" % args, 'green')
        else:
            cprint("[!] check args!", 'red')


def rshell():
    s = RShell()
    s.cmdloop()
    # def complete_find(self):
        # pass