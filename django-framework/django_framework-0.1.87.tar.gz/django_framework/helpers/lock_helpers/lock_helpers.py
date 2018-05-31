import arrow
import time

import os
import zc.lockfile




class LockFile(object):
    '''Basic wrapper around the zc.lockfile files.  Used as semaphore
    to prevent multiple processes from running at the same time.
    
    Setting the variable: max_locks to int greater than 1, will let this become a
    "counting semaphore (where we count locked files)", up to X number of resources can be created.  Defaults to 1
        - when using: counting semaphore, file checking will done by appending X, for X in range(max_locks), to the filename
    
    Upon __exit__, will attempt to clean up files or close existing locks.
    SigInt exits may cause left over files - this will still release the locks though files may still exist.
    
    Ways of using:
    ============
    lock = LockFile(lock_name = 'testlock')
    lock.lock()
    lock.unlock()
    
    ============
    with LockFile(lock_name = 'testlock') as lock:
        do_stuff()
    ============
    '''
    
    
    LOCK_MESSAGE = """Locked at (utc via system clock): {lock_time} 
                      name: {name}
                      """
                      
    UNLOCK_MESSAGE = """Unlocked at (utc via system clock): {lock_time} 
                      name: {name}
                      """
    
    
    def __init__(self, lock_name, 
                 name = None, 
                 max_locks = None, 
                 remove_file = True,
                 filepath = None, 
                 lock_message = None, 
                 unlock_message = None,
                 ):
        
        self.name = name  # name to be placed inside file, typically whoever called it!
        
        self.filename = lock_name  # the name of this lock file
        
        self.filepath = filepath   # location of the file
        
        self.remove_file = remove_file # should remove file or not.  by default zc.lockfile will not remove files.
                                       # The lock file is not removed.  It is left behind:
                                       # setting to True, will remove file.
        
        # used for counting semaphore if multiple locks are needed.
        self.max_locks = max_locks  
        if self.max_locks == None:
            self.max_locks = 1
        
        if self.max_locks < 1:
            raise ValueError('Must have at least one possible lock')
        
        
        self.lock_message = lock_message 
        self.unlock_message = unlock_message
        
        
        # internal states
        self._is_locked = False
        self._best_lock = None
        
        
    def _get_lock_message(self):
        '''Get the lock message to be placed inside lock file.'''
        if self.lock_message == None:
            message = self.LOCK_MESSAGE
        else:
            message = self.lock_message
            
        message = message.format(lock_time = arrow.utcnow(), name = self.name)
        return message
    
    def _generate_filename(self, lock_number):
        '''Create the lock file filename. 
        TODO:  take into account filepath when creating file!
        '''
        if lock_number == None or lock_number == 0:
            filename = self.filename
        else:
            filename, file_extension = os.path.splitext(self.filename)
            filename = '{filename}_{lock_number}'.format(filename = filename, lock_number = lock_number)
            if file_extension != '':
                filename += file_extension
                
        if self.filepath:
            filename = self.filepath + filename
        
        return filename
    
    def generate_best_filename(self):
        '''Get the existing filename that was used in the past!
        '''
        if self._is_locked == False:
            raise ValueError('Cannot request the best filename if there is no lock!')
        return self._generate_filename(lock_number = self._best_lock)
    
    def lock(self):
        '''Get the lock file.  If failure, will raise an error
        - Failure can be due to read/write permissions to the location
        - Failure to retrieve a lock
        '''
        
        message = self._get_lock_message()
        
        for lock_number in range(self.max_locks): # iterate over possible locks!
            filename = self._generate_filename(lock_number = lock_number)
            try:
                self._lock_file = zc.lockfile.LockFile(filename, content_template = message)
                self._is_locked = True
                self._best_lock = lock_number
            except zc.lockfile.LockError:
                pass
        
        if self._is_locked == False:
            raise zc.lockfile.LockError('Requested a lock but failed')
        
    def _get_unlock_message(self):
        
        if self.unlock_message == None:
            message = self.UNLOCK_MESSAGE
        else:
            message = self.unlock_message
            
        message = message.format(lock_time = arrow.utcnow(), name = self.name)
        return message
    
    def unlock(self):
        
        self._lock_file.close() # release the existing lock
        
        # used to write a message to the file about when it was unlocked
        # not as useful when the file is supposed to be removed
        message = self._get_unlock_message()
        filename = self.generate_best_filename()
        self._lock_file = zc.lockfile.LockFile(filename, content_template = message)
        self._lock_file.close() # release the lock
        
        # set internal variables
        self._is_locked = False
        
        # remove the lock file
        if self.remove_file == True:
            os.remove(filename)
    
    
    def __enter__(self):
        '''Called when entering a With loop:
        Get a lock if possible, throw an error if not!
        
        very odd behavior if you doing something silly like:
        
        s = LockFile(lock_name = 'test_lock', max_locks = 2)
        with s:
            print(s)
        
        '''
        if self._is_locked == True:
            raise zc.lockfile.LockFile('This instance already has a lock.  You cannot lock more than once.')
        else:
            self.lock()
        return self
    
    def __exit__(self, exception_type, exception_val, trace):
        '''Called when exiting a With Loop:
        with LockFile(lock_name = 'test_lock') as lf
        
        This is different than __del__, as __del__ is called when removing from scope.
        
        '''
        self._cleanup()
        
        if exception_type is not None:
            raise
        
    def __del__(self):
        '''Called when the instance is deleted by Garbage Collect.
        We want to make sure that the lock is released!
        '''
        self._cleanup()
        
    def _cleanup(self):
        ''''''
        try:
            if self._is_locked == True: # otherwise attemping to unlock file will cause the "unlock" time to change again!
                self.unlock()
        except Exception:
            raise
        
if __name__ == '__main__':
    
    s = LockFile(lock_name = 'test_lock', filepath = './test/', max_locks = 2)
    with s:
        print(s)
        

        time.sleep(10)
    