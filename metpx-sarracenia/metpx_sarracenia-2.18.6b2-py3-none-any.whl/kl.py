#!/usr/bin/env python3

import os.path
import sys

k=os.path.realpath( __file__ )
k= __file__ 
k=os.path.normpath(os.path.realpath( __file__ ))

print( "k=%s realpath=%s \n" % 
  (  __file__, os.path.realpath( __file__ ) ) )
