
import time
import arrow

from django.core.management.base import BaseCommand, CommandError

from django_framework.helpers.lock_helpers.lock_helpers import LockFile

class LockMixinCommand(object):
    MAX_LOCKS = 1
    
    LOCK_NAME = 'command_management_lock'
    LOCK_DESCRIPTION = 'default'
    
    LOCK_FILE_PATH = None
    
    @property
    def lock_file(self):
        if hasattr(self, '_lock_file') == False:
            self._lock_file = LockFile(
                lock_name = self.LOCK_NAME, 
                 name = self.LOCK_DESCRIPTION, 
                 max_locks = self.MAX_LOCKS, 
                 remove_file = True,
                 
                 filepath = self.LOCK_FILE_PATH, 
                 lock_message = None, 
                 unlock_message = None)
        
        return self._lock_file

    def lock(self):
        self.lock_file.lock()
        
    def unlock(self):
        self.lock_file.unlock()
