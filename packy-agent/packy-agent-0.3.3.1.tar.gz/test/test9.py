from filelock import FileLock
import time

file_lock = FileLock('/tmp/dumb.lock')
print 'Before lock'
with file_lock.acquire(timeout=1):
    import os
    os.system('(sleep 30; date > /tmp/haha) &')
print 'After lock'
