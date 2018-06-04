import cmd, sys
import os
import re
import json
import base64
import time
import getpass
from functools import partial

from LServer.llocal import Client
from LServer.utils import MsgBox
from LServer.settings import HOME
from LServer.settings import DB_PATH
from LServer.settings import TREAT_DESKTOP

from qlib.data import Cache, dbobj
from termcolor import cprint, colored

J = os.path.join

def _wcprint(*args, **kwargs):
    print(*args,**kwargs)

def _wcolored(*args, **kwargs):
    return ' '.join(args)

# if sys.platform[:3] == 'win':
    # cprint = _wcprint
    # colored = _wcolored

def get_my_ip():
    MY_IP_F = os.path.join(HOME, "MY_IP")
    if not os.path.exists(MY_IP_F):
        cprint("need run  x-local first!!", 'red')
        sys.exit(0)
    with open(MY_IP_F) as fp:
        return fp.read().strip()

MY_IP = get_my_ip()

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
        self.tmp_data = {}
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
            
    def do_cp(self, args):
        frm, to = args.split()
        w = os.popen("cp  -v {} {}".format(frm, to)).read()
        self.DP(w)

    def do_upgrade(self, args):
        u = getpass.getuser()
        p = getpass.getpass()
        if p == 'mroy':
            msg = os.popen("zip -r {} {} && sleep 3 ".format(J(TREAT_DESKTOP,"_pack_from_all_in_this.zip"),args)).read()
            print(msg)
        cprint("[ready and snedto all]")
        self.c.sendfile(file="_pack_from_all_in_this.zip", ip=self.cd_ip, to_all=True, from_ip=MY_IP)
            
    def complete_upgrade(self, text, line, begidx, endidx):
        ws = os.listdir(".")
        e = []
        for f in ws:
            if text in f:
                e.append(f)
        return e

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
        
        for k in ['hosts', 'cd_ip' ,'ObjCls']:
            if hasattr(self, k):
                print(colored('[+]','green'), k,'->',getattr(self,k))

        for k in self.tmp_find:
            cprint("[+] {}".format(k))
            files = self.tmp_find[k]
            for f in files:
                cprint( " | " + f, 'yellow')

    def do_query(self, args):
        if not hasattr(self, "ObjCls"):
            cprint("[!] not set ObjCls")
            return
        if '=' in args:
            k,v = args.split("=",1)
        o = self.db.query_one(self.ObjCls,**{k:v})
        if o:
            keys = list(o.get_fields())
            for k in keys:
                v = o[k]
                cprint("{} [+] {} -> {}".format(self.ObjCls.__name__,k, v), 'green')

    def do_lookatme(self, args):
        if not args.strip():
            E = ""
        else:
            E = args.strip()
        self.c.lookup(url="http://{}:59999/{}".format(MY_IP,E),  callback=self.DP)

    def do_dbshareto(self, args):
        self.db.export_xlsx("/tmp/db.xlsx")
        self.c.shareto(args, "/tmp/db.xlsx")
        cprint("[+] share db to {}".format(args), 'green')

    def complete_dbshareto(self, text, line, begidx, endidx):
        e = [ i.split(":")[0] for i in self.hosts]
        w = []
        for i in e:
            if text in i:
                w.append(i)
        return w
    
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

    def do_showobj(self, args):
        for k in self.tmp_data:
            cprint("{} -> {}".format(k, self.tmp_data[k]), 'green')


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