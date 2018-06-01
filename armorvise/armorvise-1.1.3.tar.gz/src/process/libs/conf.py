#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

###### global
### options
options_short = "hVp"
options_long = ["help","version","proc"]
### conf
conf_proc_root_dir = "/tmp/"
conf_proc_pid_fname = "armor_proc_"
conf_proc_log_fname = "armor_proc_"
conf_pro_pid_end = "pid"
conf_pro_log_end = "log"
conf_proc_pid_pre = conf_proc_root_dir + conf_proc_pid_fname + "{}." + conf_pro_pid_end
conf_proc_log_pre = conf_proc_root_dir + conf_proc_log_fname + "{}." + conf_pro_log_end


