#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import re
import time
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import util
help_out = """usage: armorvise "cmd"
example: armorvise "sh test.sh >/dev/null 2>&1"
optional arguments:
    -h                  help
    --help              help
    -V                  version
    --version           version
about process:
    -p                  show all processes
    --proc              show all processes
"""

version_out = """armorvise version={}"""



### cls
class console_io(object):
    def __init__(self,options):
        MY_PATH = os.path.abspath(os.path.dirname(__file__))
        EXT_PATH = "{}/../ext".format(MY_PATH)
        INFO_JSON = "conf.json"

        self.proj_info = json.loads(open(os.path.join(EXT_PATH, INFO_JSON)).read())

        # [('--help', '')]
        self.options = options
        self.deal_options()

    def deal_options(self):
        global help_out
        global version_out
        for each in self.options:
            option = each[0]
            if option in ['--help','-h']:
                print help_out
                return

            if option in ['--version','-V']:
                print version_out.format(self.proj_info["version"])
                return

            if option in ['--proc','-p']:
                res = util.get_all_proc()
                returnVal = """All Proc
PID CMD"""
                for each in res:
                    returnVal = """{}
{}""".format(returnVal,"{}")
                    line_info = "{} {}".format(each["pid"],each["cmd"])
                    returnVal = returnVal.format(line_info)

                print returnVal
                return
        
        print help_out
        return
        #raise RuntimeError("Options error!")



                













