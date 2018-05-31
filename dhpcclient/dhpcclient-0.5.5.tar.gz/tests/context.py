
"""
    Used for generating a path independent test context
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dhpcclient.hpcclient as hpcclient
import dhpcclient.requestproxy as requestproxy
import dhpcclient.taskhandler as taskhandler
import dhpcclient.task as task
import dhpcclient.tasklogger as tasklogger


