import sys
import modelx as mx
import warnings

m, s = mx.new_model(), mx.new_space('base')



def foo(x):
    return x

sub = s.new_cells()

# sub = s.new_cells()

# s.foo(3)

import pickle

# gref = m._impl._global_refs
pickle.dumps(s._impl._namespace_impl)
