
"""
    Used for generating a path independent test context
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import hpcclient.hpcclient as hpcclient
import hpcclient.requestproxy as requestproxy
import hpcclient.taskhandler as taskhandler
import hpcclient.task as task
import hpcclient.tasklogger as tasklogger


