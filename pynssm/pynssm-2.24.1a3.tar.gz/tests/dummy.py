"""
Dummy python script
"""

import time
from datetime import datetime

while True:
    msg = "[{}]: Tick!"
    print msg.format(datetime.now())
    time.sleep(1)
