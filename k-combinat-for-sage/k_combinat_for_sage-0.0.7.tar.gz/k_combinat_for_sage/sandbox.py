#!/usr/bin/env sage
# Just a place to quickly test things.  NOT part of repo.
from __future__ import print_function
import time
from sage.all import *
from testing import *
from main import *
start_time = time.time()
print('Sage loaded.  Executing stuff...')
# BEGIN!







# ALL DONE!
print('Local code completed successfully!', end='')
end_time = time.time()
elapsed_time = end_time - start_time
print(' Elapsed time = {}'.format(elapsed_time))
