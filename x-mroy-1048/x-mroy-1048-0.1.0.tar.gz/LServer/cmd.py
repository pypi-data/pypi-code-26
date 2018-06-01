import cmd, sys
import os
import re
import json
import base64
from LServer.llocal import Client
from LServer.lserver import MsgBox
from qlib.data import Cache, dbobj
from termcolor import cprint, colored


HOME = os.path.join(os.path.join(os.getenv('HOME'), '.config'), 'treatbook')
DB_PATH =  os.path.join(HOME, "database.sql")

class RShell(cmd.Cmd):

    def __init__(self):
        super().__init__()
        self.prompt = colored("=> ", 'red')
        self.c = Client("localhost")
        self.db = Cache(DB_PATH)
        self.hosts = set()
        self.cd_ip =  'localhost'
        self.tmp_find = []

    def do_exit(self, args):
        return True

    def _pre_find_files(self, files):
        t = json.loads(files)['res']
        if isinstance(t, list):
            self.tmp_find = t
        else:
            if '127.0.0.1' in t:
                t = t['127.0.0.1']

            self.tmp_find = t

    def do_find(self, args):
        self.c.find(file=args, callback=self._pre_find_files)
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


    def do_download(self, args):
        self.c.file(self.cd_ip, args)
        cprint('[Download]', 'green')

    def complete_download(self, text, line, begidx, endidx):
        fs = []
        for f in self.tmp_find:
            if text in f:
                fs.append(f)
        return fs

    def DP(self, args):
        if isinstance(args, bytes):
            cprint("[+] {}".format(json.loads(args)['res']), 'green')
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

    def do_query(self, args):
        if not hasattr(self, "ObjCls"):
            cprint("[!] not set ObjCls")
            return
        if '=' in args:
            k,v = args.split("=",1)
        o = self.cache.query_one(self.ObjCls,**{k:v})
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