import pickle
import modelx as mx


"""
    derived<-----------base
     |  +---fibo       | +----fibo
    child---fibo      child---fibo
     |                 |
    nested--fibo      nested--fibo
"""

def fibo(x):
    if x == 0 or x == 1:
        return x
    else:
        return fibo(x - 1) + fibo(x - 2)


model, base = mx.new_model(), mx.new_space('base')
child = base.new_space('child')
nested = child.new_space('nested')
derived = model.new_space('derived', bases=base)
base.new_cells(formula=fibo)
child.new_cells(formula=fibo)
nested.new_cells(formula=fibo)

basechild_impl = model.base.child._impl

dump = pickle.dumps(model)
model = pickle.loads(dump)

# model.derived.child._impl._spaces
child_space = model.derived.child._impl._derived_spaces
assert 'nested' in model.derived.child.spaces

basechild_impl = model.base.child._impl

basechild = model.base.child
# del model.base.child.nested
del basechild.nested
assert 'nested' not in model.base.child.spaces
assert 'nested' not in model.derived.child.spaces