"""
This library can send other data types via socket.
Only for python versions that are higher than 2.7.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import receive
import send
from datatype import sendableData
import pickle
